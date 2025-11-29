import psycopg2
from psycopg2 import pool
from cryptography.fernet import Fernet
from config import DB_CONFIG, ENCRYPTION_KEY

class Database:
    def __init__(self):
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10, **DB_CONFIG
        )
        # REQUISITO 3: Sistema de encriptación
        self.cipher = Fernet(ENCRYPTION_KEY)
    
    def get_connection(self):
        return self.connection_pool.getconn()
    
    def release_connection(self, conn):
        self.connection_pool.putconn(conn)
    
    # REQUISITO 3: Encriptación de datos sensibles
    def encriptar(self, texto):
        if texto is None:
            return None
        return self.cipher.encrypt(texto.encode())
    
    def desencriptar(self, datos_enc):
        if datos_enc is None:
            return None
        return self.cipher.decrypt(bytes(datos_enc)).decode()