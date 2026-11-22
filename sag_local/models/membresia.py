import datetime


class Membresia:
    """Membresía vendida a un cliente. Incluye su estado y fechas de vigencia."""

    # Estados válidos
    ACTIVA = "activa"
    VENCIDA = "vencida"
    CANCELADA = "cancelada"

    def __init__(
        self,
        codigo_membresia: str,
        fecha_inicio: datetime.date,
        fecha_vencimiento: datetime.date,
        estado: str,
        fecha_cancelacion: datetime.date | None,
        motivo_cancelacion: str | None,
        codigo_cliente: int,
        codigo_tipo: int,
        codigo_empleado: int,
    ):
        self.codigo_membresia = codigo_membresia
        self.fecha_inicio = fecha_inicio
        self.fecha_vencimiento = fecha_vencimiento
        self.estado = estado
        self.fecha_cancelacion = fecha_cancelacion
        self.motivo_cancelacion = motivo_cancelacion
        self.codigo_cliente = codigo_cliente
        self.codigo_tipo = codigo_tipo
        self.codigo_empleado = codigo_empleado

    def __repr__(self):
        return (
            f"Membresia(codigo='{self.codigo_membresia}', estado='{self.estado}', "
            f"vencimiento={self.fecha_vencimiento})"
        )
