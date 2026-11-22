import datetime


class AsistenciaGym:
    """Registro de la asistencia de un cliente al gimnasio."""

    def __init__(
        self,
        codigo_asistencia: int,
        fecha: datetime.date,
        hora: datetime.time,
        codigo_cliente: int,
        codigo_rutina: int | None = None,
    ):
        self.codigo_asistencia = codigo_asistencia
        self.fecha = fecha
        self.hora = hora
        self.codigo_cliente = codigo_cliente
        self.codigo_rutina = codigo_rutina   # opcional (RF-11)

    def __repr__(self):
        return (
            f"AsistenciaGym(codigo={self.codigo_asistencia}, "
            f"cliente={self.codigo_cliente}, fecha={self.fecha}, "
            f"hora={self.hora})"
        )
