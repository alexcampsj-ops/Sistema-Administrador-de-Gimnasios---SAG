import datetime
from config.db import get_connection
from models.cliente import Cliente
from models.celular import Celular


class ClienteService:
    """CRUD de clientes y sus celulares (RF-05, RF-20)."""

    def registrar(
        self,
        nombre: str,
        apellido_paterno: str,
        apellido_materno: str,
        fecha_nacimiento: datetime.date,
        colonia: str,
        calle: str,
        celulares: list[str],
    ) -> int:
        """Inserta un cliente nuevo junto con sus números de celular.

        Devuelve el codigo_cliente generado por la base de datos (AUTO_INCREMENT).
        Si algo falla, se hace rollback para no dejar datos incompletos.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            # Inserta el cliente; estado=1 significa activo
            cursor.execute(
                """
                INSERT INTO CLIENTE
                    (nombre, apellido_paterno, apellido_materno,
                     fecha_nacimiento, colonia, calle, estado)
                VALUES (%s, %s, %s, %s, %s, %s, 1)
                """,
                (nombre, apellido_paterno, apellido_materno,
                 fecha_nacimiento, colonia, calle),
            )
            # lastrowid obtiene el ID generado automáticamente por MySQL
            codigo_cliente = cursor.lastrowid
            # Inserta cada número de celular asociado al cliente recién creado
            for numero in celulares:
                cursor.execute(
                    "INSERT INTO CELULAR (numero, codigo_cliente) VALUES (%s, %s)",
                    (numero, codigo_cliente),
                )
            # Confirma todos los cambios en la base de datos en una sola transacción
            conn.commit()
            return codigo_cliente
        except Exception:
            # Si algo falla, deshace todos los cambios de esta transacción
            conn.rollback()
            raise
        finally:
            conn.close()

    def buscar(self, termino: str) -> list[Cliente]:
        """Busca clientes por nombre, apellido paterno o número de celular exacto.

        Usa LIKE para búsqueda parcial en nombre/apellido y = para celular exacto.
        DISTINCT evita duplicados cuando un cliente tiene varios celulares
        que coincidan con el término.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT DISTINCT c.*
                FROM CLIENTE c
                LEFT JOIN CELULAR cel ON c.codigo_cliente = cel.codigo_cliente
                WHERE c.nombre LIKE %s
                   OR c.apellido_paterno LIKE %s
                   OR cel.numero = %s
                """,
                # Los % alrededor del término permiten búsqueda parcial (ej. "Mar" encuentra "Maria")
                (f"%{termino}%", f"%{termino}%", termino),
            )
            # Convierte cada fila dict en un objeto Cliente
            return [self._row_to_cliente(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def obtener_por_id(self, codigo_cliente: int) -> Cliente | None:
        """Busca un cliente exacto por su código. Devuelve None si no existe."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM CLIENTE WHERE codigo_cliente = %s",
                (codigo_cliente,),
            )
            row = cursor.fetchone()
            # Si no hay fila, devuelve None; si hay, la convierte en objeto Cliente
            return self._row_to_cliente(row) if row else None
        finally:
            conn.close()

    def editar(self, codigo_cliente: int, **campos) -> None:
        """Actualiza solo los campos indicados del cliente (actualización parcial).

        Usa **campos (kwargs) para recibir un número variable de columnas a actualizar.
        Construye dinámicamente la cláusula SET del UPDATE.
        Ejemplo de uso: editar(1, colonia="Centro", calle="Av. 5")
        """
        if not campos:
            # Si no se pasa ningún campo, no hay nada que actualizar
            return
        # Construye "colonia = %s, calle = %s" a partir de los keys del dict
        set_clause = ", ".join(f"{col} = %s" for col in campos)
        # Los valores van primero, el ID al final (para el WHERE)
        valores = list(campos.values()) + [codigo_cliente]
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE CLIENTE SET {set_clause} WHERE codigo_cliente = %s",
                valores,
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def cambiar_estado(self, codigo_cliente: int, estado: bool) -> None:
        """Da de baja (False) o reactiva (True) a un cliente.

        Convierte el bool a int porque MySQL almacena el estado como TINYINT (0 ó 1).
        """
        self.editar(codigo_cliente, estado=int(estado))

    def listar_celulares(self, codigo_cliente: int) -> list[Celular]:
        """Devuelve todos los celulares registrados para un cliente."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM CELULAR WHERE codigo_cliente = %s",
                (codigo_cliente,),
            )
            return [
                Celular(r["codigo_celular"], r["numero"], r["codigo_cliente"])
                for r in cursor.fetchall()
            ]
        finally:
            conn.close()

    def agregar_celular(self, numero: str, codigo_cliente: int) -> None:
        """Agrega un nuevo número de celular a un cliente existente."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO CELULAR (numero, codigo_cliente) VALUES (%s, %s)",
                (numero, codigo_cliente),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    @staticmethod
    def _row_to_cliente(row: dict) -> Cliente:
        """Convierte un diccionario (fila de la BD) en un objeto Cliente.

        Es un método privado de utilidad usado internamente por los otros métodos.
        El prefijo _ indica que no debe llamarse desde fuera de la clase.
        """
        return Cliente(
            codigo_cliente=row["codigo_cliente"],
            nombre=row["nombre"],
            apellido_paterno=row["apellido_paterno"],
            apellido_materno=row["apellido_materno"],
            fecha_nacimiento=row["fecha_nacimiento"],
            colonia=row["colonia"],
            calle=row["calle"],
            estado=bool(row["estado"]),  # Convierte 0/1 a False/True
        )
