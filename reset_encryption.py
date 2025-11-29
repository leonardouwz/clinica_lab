"""
Script de utilidad para resetear la clave de encriptación
ADVERTENCIA: Esto hará que todos los datos encriptados sean ilegibles
Solo usar si se perdió la clave y se necesita empezar de nuevo
"""

import os
import psycopg2
from cryptography.fernet import Fernet
from config import DB_CONFIG

def reset_encryption():
    print("="*70)
    print("RESETEAR CLAVE DE ENCRIPTACIÓN")
    print("="*70)
    print("\nADVERTENCIA")
    print("Este proceso:")
    print("1. Eliminará TODOS los pacientes de la base de datos")
    print("2. Generará una nueva clave de encriptación")
    print("3. NO podrá recuperar los datos anteriores")
    print()
    
    confirmacion = input("¿Está seguro que desea continuar? (escriba 'SI' para confirmar): ")
    
    if confirmacion != "SI":
        print("Operación cancelada.")
        return
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Eliminar todos los pacientes (esto eliminará órdenes y resultados en cascada si hay FK)
        print("\n1. Eliminando pacientes existentes...")
        cursor.execute("DELETE FROM pacientes")
        conn.commit()
        print("   ✓ Pacientes eliminados")
        
        # Generar nueva clave
        print("\n2. Generando nueva clave de encriptación...")
        new_key = Fernet.generate_key()
        
        # Guardar nueva clave
        key_file = 'encryption.key'
        with open(key_file, 'wb') as f:
            f.write(new_key)
        
        print(f"   ✓ Nueva clave guardada en '{key_file}'")
        print(f"   ✓ Clave: {new_key.decode()}")
        
        print("\n" + "="*70)
        print("RESET COMPLETADO EXITOSAMENTE")
        print("="*70)
        print("\nAhora puede:")
        print("1. Reiniciar la aplicación")
        print("2. Registrar nuevos pacientes")
        print("\nGuarde el archivo 'encryption.key' de forma segura")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\nError: {e}")
        if 'conn' in locals():
            conn.rollback()

if __name__ == '__main__':
    reset_encryption()