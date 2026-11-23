import mysql.connector
from mysql.connector import Error


# Configuración de la conexión a MySQL.
# Ajusta estos valores según tu entorno antes de ejecutar el programa.
_CONFIG = {
    "host": "localhost",       # Dirección del servidor de base de datos
    "port": 3306,              # Puerto estándar de MySQL
    "database": "sag_db",      # Nombre de la base de datos del proyecto
    "user": "root",            # Usuario de MySQL
    "password": "",            # Contraseña del usuario (vacía por defecto)
    "charset": "utf8mb4",      # Codificación de caracteres (soporta emojis y acentos)
}


def get_connection():
    """Crea y devuelve una conexión activa a MySQL.

    Uso recomendado (siempre cerrar la conexión en un bloque finally):
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)  # dictionary=True hace que
            ...                                    # cada fila sea un dict en
        finally:                                   # lugar de una tupla
            conn.close()

    Lanza ConnectionError si no se puede establecer la conexión.
    """
    try:
        # Desempaqueta el diccionario _CONFIG como argumentos con nombre
        conn = mysql.connector.connect(**_CONFIG)
        return conn
    except Error as e:
        # Envuelve el error de MySQL en un ConnectionError más descriptivo
        raise ConnectionError(f"No se pudo conectar a la base de datos: {e}")
