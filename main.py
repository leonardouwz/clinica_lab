"""
ClinicalLabManager - Sistema de Gestión de Laboratorios Clínicos
Punto de entrada principal
"""

from interfaz import ClinicalLabManager

if __name__ == '__main__':
    try:
        app = ClinicalLabManager()
        app.run()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        input("Presione Enter para salir...")