class Especialidad:
    """Especialidad de una clase (ej. Yoga, Spinning, Zumba)."""

    def __init__(self, codigo_especialidad: int, nombre: str, descripcion: str):
        self.codigo_especialidad = codigo_especialidad
        self.nombre = nombre
        self.descripcion = descripcion

    def __repr__(self):
        return (
            f"Especialidad(codigo_especialidad={self.codigo_especialidad}, "
            f"nombre='{self.nombre}')"
        )
