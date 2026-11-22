class Empleado:
    """Representa a un empleado del gimnasio con su rol y credenciales."""

    def __init__(
        self,
        codigo_empleado: int,
        nombre: str,
        usuario: str,
        contrasena: str,
        correo: str,
        estado: bool,
        codigo_rol: int,
    ):
        self.codigo_empleado = codigo_empleado
        self.nombre = nombre
        self.usuario = usuario
        self.contrasena = contrasena
        self.correo = correo
        self.estado = estado          # True = activo, False = inactivo
        self.codigo_rol = codigo_rol

    def __repr__(self):
        return (
            f"Empleado(codigo_empleado={self.codigo_empleado}, "
            f"nombre='{self.nombre}', usuario='{self.usuario}', "
            f"estado={self.estado}, codigo_rol={self.codigo_rol})"
        )
