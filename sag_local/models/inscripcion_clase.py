import datetime


class InscripcionClase:
    """Inscripción de un cliente a una clase grupal."""

    ACTIVA = "activa"
    CANCELADA = "cancelada"

    def __init__(
        self,
        codigo_inscripcion: int,
        fecha: datetime.date,
        estado: str,
        observaciones: str | None,
        codigo_cliente: int,
        codigo_clase: int,
    ):
        self.codigo_inscripcion = codigo_inscripcion
        self.fecha = fecha
        self.estado = estado
        self.observaciones = observaciones
        self.codigo_cliente = codigo_cliente
        self.codigo_clase = codigo_clase

    def __repr__(self):
        return (
            f"InscripcionClase(codigo={self.codigo_inscripcion}, "
            f"cliente={self.codigo_cliente}, clase={self.codigo_clase}, "
            f"estado='{self.estado}')"
        )
