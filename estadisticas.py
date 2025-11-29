from database import Database

def obtener_estadisticas_periodo(fecha_inicio, fecha_fin):
    """
    REQUISITO 6: Optimizar consultas de estadísticas por período
    """
    db = Database()
    conn = db.get_connection()
    
    try:
        with conn.cursor() as cursor:
            # REQUISITO 2: Consulta optimizada con índices en fecha
            cursor.execute("""
                SELECT 
                    ta.nombre AS analisis,
                    COUNT(*) AS total_realizados,
                    ROUND(AVG(r.valor), 2) AS promedio,
                    MIN(r.valor) AS minimo,
                    MAX(r.valor) AS maximo,
                    SUM(CASE WHEN r.fuera_rango = TRUE THEN 1 ELSE 0 END) AS fuera_rango_count,
                    ROUND(
                        SUM(CASE WHEN r.fuera_rango = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
                        2
                    ) AS porcentaje_fuera_rango
                FROM resultados r
                JOIN tipos_analisis ta ON r.tipo_analisis_id = ta.id
                WHERE r.fecha_resultado BETWEEN %s AND %s
                AND r.valor IS NOT NULL
                GROUP BY ta.id, ta.nombre
                ORDER BY total_realizados DESC
            """, (fecha_inicio, fecha_fin))
            
            return cursor.fetchall()
    finally:
        db.release_connection(conn)


def obtener_estadisticas_paciente(paciente_id):
    """
    Estadísticas de un paciente específico
    """
    db = Database()
    conn = db.get_connection()
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    ta.nombre,
                    r.valor,
                    r.fecha_resultado,
                    r.fuera_rango,
                    ta.valor_min,
                    ta.valor_max,
                    ta.unidad
                FROM resultados r
                JOIN ordenes o ON r.orden_id = o.id
                JOIN tipos_analisis ta ON r.tipo_analisis_id = ta.id
                WHERE o.paciente_id = %s
                AND r.valor IS NOT NULL
                ORDER BY r.fecha_resultado DESC
                LIMIT 50
            """, (paciente_id,))
            
            return cursor.fetchall()
    finally:
        db.release_connection(conn)