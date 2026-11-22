import storage as db
from models.empleado import Empleado

MAX_INTENTOS = 3


class AuthService:
    """Login en memoria (RF-01, RF-02, RF-03)."""

    def login(self, usuario: str, contrasena: str, nombre_rol: str) -> Empleado | None:
        # Buscar el codigo_rol que coincide con nombre_rol
        rol = next((r for r in db.roles if r["nombre"] == nombre_rol), None)
        if rol is None:
            return None

        row = next(
            (
                e for e in db.empleados
                if e["usuario"] == usuario
                and e["contrasena"] == contrasena
                and e["estado"]
                and e["codigo_rol"] == rol["codigo_rol"]
            ),
            None,
        )
        if row is None:
            return None

        return Empleado(
            codigo_empleado=row["codigo_empleado"],
            nombre=row["nombre"],
            usuario=row["usuario"],
            contrasena=row["contrasena"],
            correo=row["correo"],
            estado=row["estado"],
            codigo_rol=row["codigo_rol"],
        )
