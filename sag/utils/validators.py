import datetime
import re


def validar_celular(numero: str) -> bool:
    """Verifica que el número tenga exactamente 10 dígitos.

    Usa una expresión regular: \\d = cualquier dígito, {10} = exactamente 10 veces.
    fullmatch exige que TODA la cadena coincida (no solo una parte).
    """
    return bool(re.fullmatch(r"\d{10}", numero))


def validar_fecha(texto: str) -> datetime.date | None:
    """Convierte una cadena 'YYYY-MM-DD' a un objeto date.

    Devuelve None si el formato es inválido, en lugar de lanzar una excepción,
    para que la vista pueda pedir al usuario que lo intente de nuevo.
    """
    try:
        # fromisoformat acepta el formato estándar ISO: 'YYYY-MM-DD'
        return datetime.date.fromisoformat(texto)
    except ValueError:
        # El texto no tiene el formato correcto
        return None


def validar_correo(correo: str) -> bool:
    """Validación básica de formato de correo electrónico.

    La expresión regular verifica que exista:
      - uno o más caracteres que no sean @ ni espacio
      - un @
      - uno o más caracteres que no sean @ ni espacio
      - un punto
      - uno o más caracteres que no sean @ ni espacio
    """
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo))


def validar_hora(texto: str) -> datetime.time | None:
    """Convierte una cadena 'HH:MM' a un objeto time.

    Devuelve None si el formato es inválido.
    """
    try:
        # Separa horas y minutos por el carácter ':'
        h, m = texto.split(":")
        # Crea un objeto time con los valores enteros
        return datetime.time(int(h), int(m))
    except (ValueError, AttributeError):
        # ValueError: números fuera de rango (ej. hora 25)
        # AttributeError: si texto es None u otro tipo que no tiene .split
        return None


def confirmar(mensaje: str = "¿Confirmar? (S/N): ") -> bool:
    """Pide al usuario una confirmación de tipo S/N antes de ejecutar una acción.

    Devuelve True solo si el usuario escribe 'S' o 's'.
    Se usa en todas las operaciones de escritura (insertar, editar, eliminar)
    para evitar cambios accidentales.
    """
    respuesta = input(mensaje).strip().upper()
    return respuesta == "S"
