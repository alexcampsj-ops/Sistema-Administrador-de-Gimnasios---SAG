from config.db import get_connection
from models.empleado import Empleado

# Número máximo de intentos de login antes de bloquear el acceso
MAX_INTENTOS = 3


class AuthService:
    """Gestiona el inicio y cierre de sesión de los empleados (RF-01, RF-02, RF-03)."""

    def login(self, usuario: str, contrasena: str, nombre_rol: str) -> Empleado | None:
        """Valida las credenciales del empleado contra la base de datos.

        Busca un empleado activo (estado=1) cuyo usuario, contraseña y rol
        coincidan con los datos proporcionados.

        Devuelve el objeto Empleado si las credenciales son correctas,
        o None si no se encuentra ninguna coincidencia.

        Nota: el control del número de intentos se maneja en la vista (menu_inicio).
        """
        # Abre la conexión a la base de datos
        conn = get_connection()
        try:
            # dictionary=True hace que cada fila del resultado sea un dict
            # en lugar de una tupla, facilitando el acceso por nombre de columna
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
                # Los %s son parámetros seguros que previenen inyección SQL
                (usuario, contrasena, nombre_rol),
            )
            row = cursor.fetchone()  # Trae solo la primera (y única) fila
            if row is None:
                # No existe ningún empleado con esas credenciales
                return None
            # Convierte el dict de la BD en un objeto Empleado
            return Empleado(
                codigo_empleado=row["codigo_empleado"],
                nombre=row["nombre"],
                usuario=row["usuario"],
                contrasena=row["contrasena"],
                correo=row["correo"],
                estado=bool(row["estado"]),  # Convierte 0/1 a False/True
                codigo_rol=row["codigo_rol"],
            )
        finally:
            # Siempre se cierra la conexión, aunque ocurra un error
            conn.close()
