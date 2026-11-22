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
        """Inserta un empleado nuevo. Devuelve su codigo_empleado."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO EMPLEADO
                    (nombre, usuario, contrasena, correo, estado, codigo_rol)
                VALUES (%s, %s, %s, %s, 1, %s)
                """,
                (nombre, usuario, contrasena, correo, codigo_rol),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def editar(self, codigo_empleado: int, **campos) -> None:
        if not campos:
            return
        set_clause = ", ".join(f"{col} = %s" for col in campos)
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
        self.editar(codigo_empleado, estado=int(estado))

    def listar(self) -> list[Empleado]:
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM EMPLEADO ORDER BY nombre")
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
        """Inserta o reemplaza el horario de un empleado para un día (RF-19)."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            # Un solo horario por día por empleado
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
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM HORARIO WHERE codigo_empleado = %s ORDER BY dia",
                (codigo_empleado,),
            )
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
        return Empleado(
            codigo_empleado=row["codigo_empleado"],
            nombre=row["nombre"],
            usuario=row["usuario"],
            contrasena=row["contrasena"],
            correo=row["correo"],
            estado=bool(row["estado"]),
            codigo_rol=row["codigo_rol"],
        )
