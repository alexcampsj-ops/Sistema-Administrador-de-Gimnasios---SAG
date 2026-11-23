import datetime


def calcular_edad(fecha_nacimiento: datetime.date) -> int:
    """Calcula la edad en años a partir de la fecha de nacimiento."""
    hoy = datetime.date.today()
    # Resta el año de nacimiento al año actual para obtener la edad base
    edad = hoy.year - fecha_nacimiento.year
    # Si hoy es antes del cumpleaños en este año, se resta 1
    # porque la persona aún no ha cumplido años
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return edad


def formatear_fecha(fecha: datetime.date | None) -> str:
    """Devuelve la fecha como 'DD/MM/YYYY' o '—' si es None.

    Se usa para mostrar fechas en las tablas de la consola
    con un formato legible en español.
    """
    if fecha is None:
        # Si no hay fecha (campo opcional en BD), mostrar un guión
        return "—"
    # strftime formatea la fecha según la máscara indicada
    return fecha.strftime("%d/%m/%Y")


def dias_restantes(fecha_vencimiento: datetime.date) -> int:
    """Calcula los días que quedan hasta el vencimiento de una membresía.

    Devuelve un número negativo si la membresía ya expiró.
    Ejemplo: si vence en 5 días devuelve 5; si venció hace 3 días devuelve -3.
    """
    # La resta de dos objetos date devuelve un timedelta;
    # .days extrae el número entero de días
    return (fecha_vencimiento - datetime.date.today()).days
