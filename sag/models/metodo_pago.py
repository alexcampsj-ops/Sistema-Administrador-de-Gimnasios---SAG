class MetodoPago:
    """Método de pago disponible en el gimnasio (ej. Efectivo, Tarjeta de débito)."""

    def __init__(self, codigo_metodo: int, nombre: str, estado: bool):
        self.codigo_metodo = codigo_metodo
        self.nombre = nombre
        self.estado = estado          # True = activo, False = inactivo

    def __repr__(self):
        return (
            f"MetodoPago(codigo_metodo={self.codigo_metodo}, "
            f"nombre='{self.nombre}', estado={self.estado})"
        )
