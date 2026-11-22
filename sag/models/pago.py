import datetime


class Pago:
    """Registro de un pago asociado a una membresía."""

    def __init__(
        self,
        codigo_pago: int,
        fecha: datetime.date,
        monto: float,
        codigo_membresia: str,
        codigo_metodo: int,
    ):
        self.codigo_pago = codigo_pago
        self.fecha = fecha
        self.monto = monto
        self.codigo_membresia = codigo_membresia
        self.codigo_metodo = codigo_metodo

    def __repr__(self):
        return (
            f"Pago(codigo_pago={self.codigo_pago}, monto={self.monto}, "
            f"fecha={self.fecha}, codigo_membresia='{self.codigo_membresia}')"
        )
