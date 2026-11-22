class Rol:
    """Representa un rol de acceso al sistema (Recepcionista, Entrenador, Administrador)."""

    def __init__(self, codigo_rol: int, nombre: str):
        self.codigo_rol = codigo_rol
        self.nombre = nombre

    def __repr__(self):
        return f"Rol(codigo_rol={self.codigo_rol}, nombre='{self.nombre}')"
