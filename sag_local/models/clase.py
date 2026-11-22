import datetime


class Clase:
    """Clase grupal impartida en el gimnasio."""

    def __init__(
        self,
        codigo_clase: int,
        nombre: str,
        dia: str,
        hora_inicio: datetime.time,
        hora_fin: datetime.time,
        cupo_maximo: int,
        inscritos: int,
        es_publica: bool,
        estado: bool,
        codigo_especialidad: int,
        codigo_empleado: int,
    ):
        self.codigo_clase = codigo_clase
        self.nombre = nombre
        self.dia = dia
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.cupo_maximo = cupo_maximo
        self.inscritos = inscritos
        self.es_publica = es_publica
        self.estado = estado          # True = activa, False = cerrada
        self.codigo_especialidad = codigo_especialidad
        self.codigo_empleado = codigo_empleado

    @property
    def lugares_disponibles(self) -> int:
        return self.cupo_maximo - self.inscritos

    def __repr__(self):
        return (
            f"Clase(codigo_clase={self.codigo_clase}, nombre='{self.nombre}', "
            f"dia='{self.dia}', lugares={self.lugares_disponibles})"
        )
