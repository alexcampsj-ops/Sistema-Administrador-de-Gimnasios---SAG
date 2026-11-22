class Beneficio:
    """Beneficio que puede incluir un tipo de membresía."""

    def __init__(self, codigo_beneficio: int, descripcion: str):
        self.codigo_beneficio = codigo_beneficio
        self.descripcion = descripcion

    def __repr__(self):
        return (
            f"Beneficio(codigo_beneficio={self.codigo_beneficio}, "
            f"descripcion='{self.descripcion}')"
        )
