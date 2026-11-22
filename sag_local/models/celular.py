class Celular:
    """Número de celular asociado a un cliente (un cliente puede tener varios)."""

    def __init__(self, codigo_celular: int, numero: str, codigo_cliente: int):
        self.codigo_celular = codigo_celular
        self.numero = numero              # 10 dígitos
        self.codigo_cliente = codigo_cliente

    def __repr__(self):
        return (
            f"Celular(numero='{self.numero}', "
            f"codigo_cliente={self.codigo_cliente})"
        )
