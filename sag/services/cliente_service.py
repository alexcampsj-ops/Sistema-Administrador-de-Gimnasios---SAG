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
        """Inserta un cliente nuevo con sus celulares. Devuelve el codigo_cliente."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
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
            codigo_cliente = cursor.lastrowid
            for numero in celulares:
                cursor.execute(
                    "INSERT INTO CELULAR (numero, codigo_cliente) VALUES (%s, %s)",
                    (numero, codigo_cliente),
                )
            conn.commit()
            return codigo_cliente
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def buscar(self, termino: str) -> list[Cliente]:
        """Busca clientes por nombre o por número de celular."""
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
                (f"%{termino}%", f"%{termino}%", termino),
            )
            return [self._row_to_cliente(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def obtener_por_id(self, codigo_cliente: int) -> Cliente | None:
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM CLIENTE WHERE codigo_cliente = %s",
                (codigo_cliente,),
            )
            row = cursor.fetchone()
            return self._row_to_cliente(row) if row else None
        finally:
            conn.close()

    def editar(self, codigo_cliente: int, **campos) -> None:
        """Actualiza solo los campos indicados."""
        if not campos:
            return
        set_clause = ", ".join(f"{col} = %s" for col in campos)
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
        """Da de baja (False) o reactiva (True) a un cliente."""
        self.editar(codigo_cliente, estado=int(estado))

    def listar_celulares(self, codigo_cliente: int) -> list[Celular]:
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
        return Cliente(
            codigo_cliente=row["codigo_cliente"],
            nombre=row["nombre"],
            apellido_paterno=row["apellido_paterno"],
            apellido_materno=row["apellido_materno"],
            fecha_nacimiento=row["fecha_nacimiento"],
            colonia=row["colonia"],
            calle=row["calle"],
            estado=bool(row["estado"]),
        )
