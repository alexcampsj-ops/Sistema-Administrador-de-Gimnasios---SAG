from config.db import get_connection
from models.empleado import Empleado
from models.horario import Horario


class EmpleadoService:
    """Gestión de empleados, roles y horarios (RF-17, RF-18, RF-19)."""

    # ------------------------------------------------------------------
    # Empleados
    # ------------------------------------------------------------------
    def agregar(
        self,
        nombre: str,
        usuario: str,
        contrasena: str,
        correo: str,
        codigo_rol: int,
    ) -> int:
        """Inserta un empleado nuevo en la base de datos.

        Devuelve el codigo_empleado generado por AUTO_INCREMENT.
        La base de datos validará la unicidad de usuario y correo
        (si tienen restricción UNIQUE), lanzando una excepción si ya existen.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            # estado=1 significa empleado activo al momento de crearse
            cursor.execute(
                """
                INSERT INTO EMPLEADO
                    (nombre, usuario, contrasena, correo, estado, codigo_rol)
                VALUES (%s, %s, %s, %s, 1, %s)
                """,
                (nombre, usuario, contrasena, correo, codigo_rol),
            )
            conn.commit()
            # Devuelve el ID auto-generado por MySQL
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def editar(self, codigo_empleado: int, **campos) -> None:
        """Actualiza solo los campos indicados del empleado (actualización parcial).

        Construye el UPDATE dinámicamente a partir de los kwargs recibidos.
        Ejemplo: editar(2, nombre="Carlos R.", correo="nuevo@gym.com")
        """
        if not campos:
            return
        # Genera "nombre = %s, correo = %s" según los campos recibidos
        set_clause = ", ".join(f"{col} = %s" for col in campos)
        # Los valores del SET van primero; el ID del empleado va al final para el WHERE
        valores = list(campos.values()) + [codigo_empleado]
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE EMPLEADO SET {set_clause} WHERE codigo_empleado = %s",
                valores,
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def cambiar_estado(self, codigo_empleado: int, estado: bool) -> None:
        """Activa (True) o desactiva (False) a un empleado.

        Un empleado inactivo no puede iniciar sesión en el sistema.
        """
        # int(estado) convierte True→1 y False→0 para MySQL
        self.editar(codigo_empleado, estado=int(estado))

    def listar(self) -> list[Empleado]:
        """Devuelve todos los empleados ordenados alfabéticamente por nombre."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM EMPLEADO ORDER BY nombre")
            # Convierte cada fila del resultado en un objeto Empleado
            return [self._row_to_empleado(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Horarios
    # ------------------------------------------------------------------
    def asignar_horario(
        self,
        codigo_empleado: int,
        dia: str,
        hora_inicio,
        hora_fin,
    ) -> None:
        """Inserta o reemplaza el horario de un empleado para un día (RF-19).

        Usa INSERT ... ON DUPLICATE KEY UPDATE para manejar ambos casos en una
        sola sentencia: si ya existe un horario para ese día y empleado, lo
        actualiza; si no existe, lo inserta.
        La tabla HORARIO debe tener una restricción UNIQUE en (dia, codigo_empleado).
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO HORARIO (dia, hora_inicio, hora_fin, codigo_empleado)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE hora_inicio = VALUES(hora_inicio),
                                        hora_fin    = VALUES(hora_fin)
                """,
                (dia, hora_inicio, hora_fin, codigo_empleado),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def eliminar_horario(self, codigo_horario: int) -> None:
        """Elimina un horario específico por su código."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM HORARIO WHERE codigo_horario = %s",
                (codigo_horario,),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def listar_horarios(self, codigo_empleado: int) -> list[Horario]:
        """Devuelve todos los horarios asignados a un empleado, ordenados por día."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM HORARIO WHERE codigo_empleado = %s ORDER BY dia",
                (codigo_empleado,),
            )
            # Convierte cada fila en un objeto Horario usando los campos del dict
            return [
                Horario(
                    r["codigo_horario"], r["dia"],
                    r["hora_inicio"], r["hora_fin"], r["codigo_empleado"],
                )
                for r in cursor.fetchall()
            ]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    @staticmethod
    def _row_to_empleado(row: dict) -> Empleado:
        """Convierte un diccionario (fila de la BD) en un objeto Empleado.

        Método privado de utilidad usado internamente por listar() y otros.
        """
        return Empleado(
            codigo_empleado=row["codigo_empleado"],
            nombre=row["nombre"],
            usuario=row["usuario"],
            contrasena=row["contrasena"],
            correo=row["correo"],
            estado=bool(row["estado"]),  # Convierte 0/1 a False/True
            codigo_rol=row["codigo_rol"],
        )
