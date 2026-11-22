class TipoMembresia:
    """Define un tipo de membresía: su duración en días y su monto."""

    def __init__(
        self,
        codigo_tipo: int,
        nombre: str,
        duracion_dias: int,
        monto: float,
    ):
        self.codigo_tipo = codigo_tipo
        self.nombre = nombre
        self.duracion_dias = duracion_dias
        self.monto = monto

    def __repr__(self):
        return (
            f"TipoMembresia(codigo_tipo={self.codigo_tipo}, "
            f"nombre='{self.nombre}', duracion_dias={self.duracion_dias}, "
            f"monto={self.monto})"
        )
