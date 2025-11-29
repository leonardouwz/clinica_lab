import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'clinica_lab'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'admin'),
    'port': os.getenv('DB_PORT', '5433')
}

# REQUISITO 3: Clave para encriptación (guardar de forma segura)
# IMPORTANTE: Esta clave debe ser persistente y guardada de forma segura
_env_key = os.getenv('ENCRYPTION_KEY')

if _env_key:
    # Si existe en variable de entorno, usarla
    ENCRYPTION_KEY = _env_key.encode()
else:
    # Si no existe, crear archivo con la clave
    key_file = 'encryption.key'
    
    if os.path.exists(key_file):
        # Leer clave existente
        with open(key_file, 'rb') as f:
            ENCRYPTION_KEY = f.read()
    else:
        # Generar nueva clave y guardarla
        ENCRYPTION_KEY = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(ENCRYPTION_KEY)
        print(f"NUEVA CLAVE DE ENCRIPTACIÓN GENERADA Y GUARDADA EN '{key_file}'")
        print("IMPORTANTE: Guarde este archivo de forma segura. Sin él, no podrá desencriptar los datos.")