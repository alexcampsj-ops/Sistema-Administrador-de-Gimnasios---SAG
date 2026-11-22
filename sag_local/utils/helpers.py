import datetime


def calcular_edad(fecha_nacimiento: datetime.date) -> int:
    """Calcula la edad en años a partir de la fecha de nacimiento."""
    hoy = datetime.date.today()
    edad = hoy.year - fecha_nacimiento.year
    # Ajuste si aún no cumplió años este año
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return edad


def formatear_fecha(fecha: datetime.date | None) -> str:
    """Devuelve la fecha como 'DD/MM/YYYY' o '—' si es None."""
    if fecha is None:
        return "—"
    return fecha.strftime("%d/%m/%Y")


def dias_restantes(fecha_vencimiento: datetime.date) -> int:
    """Calcula los días que quedan hasta el vencimiento de una membresía.

    Devuelve un número negativo si ya venció.
    """
    return (fecha_vencimiento - datetime.date.today()).days
