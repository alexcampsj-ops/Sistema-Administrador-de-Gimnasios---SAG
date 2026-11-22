from config.db import get_connection
from models.empleado import Empleado

MAX_INTENTOS = 3


class AuthService:
    """Gestiona el inicio y cierre de sesión de los empleados (RF-01, RF-02, RF-03)."""

    def login(self, usuario: str, contrasena: str, nombre_rol: str) -> Empleado | None:
        """Valida las credenciales contra la BD.

        Devuelve el objeto Empleado si son correctas, None si no.
        El control de intentos se maneja en la vista (menu_inicio).
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT e.*
                FROM EMPLEADO e
                INNER JOIN ROL r ON e.codigo_rol = r.codigo_rol
                WHERE e.usuario = %s
                  AND e.contrasena = %s
                  AND e.estado = 1
                  AND r.nombre = %s
                """,
                (usuario, contrasena, nombre_rol),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Empleado(
                codigo_empleado=row["codigo_empleado"],
                nombre=row["nombre"],
                usuario=row["usuario"],
                contrasena=row["contrasena"],
                correo=row["correo"],
                estado=bool(row["estado"]),
                codigo_rol=row["codigo_rol"],
            )
        finally:
            conn.close()
