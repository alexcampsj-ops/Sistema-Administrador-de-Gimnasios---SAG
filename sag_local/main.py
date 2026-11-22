"""
SAG – Sistema Administrativo de Gimnasios (versión local sin BD)
Punto de entrada del programa.

Uso:
    python main.py

Los datos viven en memoria (storage.py) y se reinician al cerrar.
Credenciales de prueba:
    Recepcionista : usuario=lgomez   contraseña=1234
    Entrenador    : usuario=cruiz    contraseña=1234
    Administrador : usuario=atorres  contraseña=1234
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from views.menu_inicio import ejecutar

if __name__ == "__main__":
    ejecutar()
