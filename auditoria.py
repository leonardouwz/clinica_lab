def registrar_auditoria(cursor, tabla, registro_id, accion, usuario, detalles, ip_address=None):
    """
    REQUISITO 4: Gestionar trazabilidad completa con auditoría de accesos
    """
    cursor.execute("""
        INSERT INTO auditoria_accesos 
        (tabla, registro_id, accion, usuario, detalles, ip_address)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (tabla, registro_id, accion, usuario, detalles, ip_address))


def consultar_auditoria_resultado(resultado_id):
    """
    Consultar historial completo de accesos a un resultado
    """
    from database import Database
    db = Database()
    conn = db.get_connection()
    
    try:
        with conn.cursor() as cursor:
            # REQUISITO 2: Consulta optimizada con índices
            cursor.execute("""
                SELECT fecha, accion, usuario, detalles, ip_address
                FROM auditoria_accesos
                WHERE tabla = 'resultados' AND registro_id = %s
                ORDER BY fecha DESC
            """, (resultado_id,))
            
            return cursor.fetchall()
    finally:
        db.release_connection(conn)
    
def consultar_auditoria_tabla(tabla, registro_id):
    """
    Consultar historial completo de accesos a cualquier tabla
    """
    from database import Database
    db = Database()
    conn = db.get_connection()
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT fecha, accion, usuario, detalles, ip_address
                FROM auditoria_accesos
                WHERE tabla = %s AND registro_id = %s
                ORDER BY fecha DESC
            """, (tabla, registro_id))
            
            return cursor.fetchall()
    finally:
        db.release_connection(conn)