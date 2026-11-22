import datetime


class Rutina:
    """Plan de entrenamiento asignado por un entrenador a un cliente."""

    def __init__(
        self,
        codigo_rutina: int,
        fecha: datetime.date,
        objetivo: str,
        observaciones: str | None,
        codigo_cliente: int,
        codigo_empleado: int,
    ):
        self.codigo_rutina = codigo_rutina
        self.fecha = fecha
        self.objetivo = objetivo
        self.observaciones = observaciones
        self.codigo_cliente = codigo_cliente
        self.codigo_empleado = codigo_empleado   # entrenador que la registró

    def __repr__(self):
        return (
            f"Rutina(codigo_rutina={self.codigo_rutina}, "
            f"cliente={self.codigo_cliente}, entrenador={self.codigo_empleado}, "
            f"fecha={self.fecha})"
        )
