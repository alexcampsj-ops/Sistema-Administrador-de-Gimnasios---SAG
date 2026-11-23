"""
SAG – Sistema Administrativo de Gimnasios
Punto de entrada del programa.

Uso:
    python main.py
"""
import sys
import os

# Agrega la carpeta actual al path de Python para que los imports
# como "from services.auth_service import ..." funcionen correctamente
# sin necesidad de instalar el proyecto como paquete.
sys.path.insert(0, os.path.dirname(__file__))

# Importa la función principal del menú de inicio
from views.menu_inicio import ejecutar

# Solo ejecuta el programa si este archivo es el punto de entrada directo
# (no si es importado como módulo desde otro archivo)
if __name__ == "__main__":
    ejecutar()
