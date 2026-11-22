import mysql.connector
from mysql.connector import Error


# Ajusta estos valores cuando tengas la base de datos lista
_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "database": "sag_db",
    "user": "root",
    "password": "",
    "charset": "utf8mb4",
}


def get_connection():
    """Devuelve una conexión activa a MySQL.

    Uso:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        ...
        conn.close()
    """
    try:
        conn = mysql.connector.connect(**_CONFIG)
        return conn
    except Error as e:
        raise ConnectionError(f"No se pudo conectar a la base de datos: {e}")
