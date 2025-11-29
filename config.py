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
# Leer ENCRYPTION_KEY desde la variable de entorno si está presente (como base64 string),
# si no, generar una nueva clave (en producción debe definirse la variable de entorno).
_env_key = os.getenv('ENCRYPTION_KEY')
if _env_key:
    ENCRYPTION_KEY = _env_key.encode()
else:
    ENCRYPTION_KEY = Fernet.generate_key()  # En producción establecer ENCRYPTION_KEY en la configuración