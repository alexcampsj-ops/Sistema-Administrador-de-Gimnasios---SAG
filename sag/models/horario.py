import datetime


class Horario:
    """Representa el horario de trabajo de un empleado en un día específico."""

    def __init__(
        self,
        codigo_horario: int,
        dia: str,
        hora_inicio: datetime.time,
        hora_fin: datetime.time,
        codigo_empleado: int,
    ):
        self.codigo_horario = codigo_horario
        self.dia = dia
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.codigo_empleado = codigo_empleado

    def __repr__(self):
        return (
            f"Horario(dia='{self.dia}', hora_inicio={self.hora_inicio}, "
            f"hora_fin={self.hora_fin}, codigo_empleado={self.codigo_empleado})"
        )
