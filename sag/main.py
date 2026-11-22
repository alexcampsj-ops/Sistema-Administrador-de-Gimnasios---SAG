"""
SAG – Sistema Administrativo de Gimnasios
Punto de entrada del programa.

Uso:
    python main.py
"""
import sys
import os

# Permite importar los módulos del proyecto sin instalar el paquete
sys.path.insert(0, os.path.dirname(__file__))

from views.menu_inicio import ejecutar

if __name__ == "__main__":
    ejecutar()
