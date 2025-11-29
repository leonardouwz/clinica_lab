"""
Script para verificar el estado de la encriptación
"""

import os
from config import ENCRYPTION_KEY, DB_CONFIG
from database import Database
import psycopg2

def verify_encryption():
    print("="*70)
    print("VERIFICACIÓN DE ENCRIPTACIÓN")
    print("="*70)
    
    # 1. Verificar clave
    print("\n1. Clave de encriptación:")
    if os.path.exists('encryption.key'):
        print("   ✓ Archivo 'encryption.key' encontrado")
    elif os.getenv('ENCRYPTION_KEY'):
        print("   ✓ Variable de entorno 'ENCRYPTION_KEY' configurada")
    else:
        print("   No se encontró clave configurada")
    
    print(f"   Clave actual: {ENCRYPTION_KEY[:20].decode()}...")
    
    # 2. Verificar conexión a BD
    print("\n2. Conexión a base de datos:")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("   ✓ Conexión exitosa")
        
        # 3. Verificar datos encriptados
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pacientes")
        total = cursor.fetchone()[0]
        print(f"\n3. Pacientes en base de datos: {total}")
        
        if total > 0:
            # Intentar desencriptar un paciente
            cursor.execute("SELECT id, nombre_enc, dni_enc FROM pacientes LIMIT 1")
            pac = cursor.fetchone()
            
            db = Database()
            try:
                nombre_enc = bytes(pac[1]) if isinstance(pac[1], memoryview) else pac[1]
                dni_enc = bytes(pac[2]) if isinstance(pac[2], memoryview) else pac[2]
                
                nombre = db.desencriptar(nombre_enc)
                dni = db.desencriptar(dni_enc)
                
                print(f"\n4. Prueba de desencriptación:")
                print(f"   ✓ Paciente ID {pac[0]} desencriptado correctamente")
                print(f"   Nombre: {nombre}")
                print(f"   DNI: {dni}")
                print("\n" + "="*70)
                print("✓ SISTEMA DE ENCRIPTACIÓN FUNCIONANDO CORRECTAMENTE")
                print("="*70)
                
            except Exception as e:
                print(f"\n4. Prueba de desencriptación:")
                print(f"    Error al desencriptar: {e}")
                print("\n" + "="*70)
                print(" ERROR: La clave no coincide con los datos encriptados")
                print("="*70)
                print("\nSoluciones posibles:")
                print("1. Si perdió la clave original, ejecute: python reset_encryption.py")
                print("2. Si tiene backup de 'encryption.key', reemplácelo")
                print("3. Restaure la variable de entorno ENCRYPTION_KEY correcta")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   Error de conexión: {e}")

if __name__ == '__main__':
    verify_encryption()