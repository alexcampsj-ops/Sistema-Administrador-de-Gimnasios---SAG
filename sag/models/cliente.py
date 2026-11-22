import datetime


class Cliente:
    """Representa a un cliente registrado en el gimnasio."""

    def __init__(
        self,
        codigo_cliente: int,
        nombre: str,
        apellido_paterno: str,
        apellido_materno: str,
        fecha_nacimiento: datetime.date,
        colonia: str,
        calle: str,
        estado: bool,
    ):
        self.codigo_cliente = codigo_cliente
        self.nombre = nombre
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.fecha_nacimiento = fecha_nacimiento
        self.colonia = colonia
        self.calle = calle
        self.estado = estado          # True = activo, False = baja

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"

    def __repr__(self):
        return (
            f"Cliente(codigo_cliente={self.codigo_cliente}, "
            f"nombre='{self.nombre_completo}', estado={self.estado})"
        )
