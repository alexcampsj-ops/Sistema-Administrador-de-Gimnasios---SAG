import datetime
import re


def validar_celular(numero: str) -> bool:
    """Verifica que el número tenga exactamente 10 dígitos."""
    return bool(re.fullmatch(r"\d{10}", numero))


def validar_fecha(texto: str) -> datetime.date | None:
    """Convierte una cadena 'YYYY-MM-DD' a date. Devuelve None si el formato es inválido."""
    try:
        return datetime.date.fromisoformat(texto)
    except ValueError:
        return None


def validar_correo(correo: str) -> bool:
    """Validación básica de formato de correo electrónico."""
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo))


def validar_hora(texto: str) -> datetime.time | None:
    """Convierte 'HH:MM' a time. Devuelve None si el formato es inválido."""
    try:
        h, m = texto.split(":")
        return datetime.time(int(h), int(m))
    except (ValueError, AttributeError):
        return None


def confirmar(mensaje: str = "¿Confirmar? (S/N): ") -> bool:
    """Pide confirmación S/N al usuario. Devuelve True solo si responde 'S' o 's'."""
    respuesta = input(mensaje).strip().upper()
    return respuesta == "S"
