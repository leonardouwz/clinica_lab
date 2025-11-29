"""
Script para testear el rendimiento de las consultas optimizadas
"""

import time
from database import Database
from datetime import datetime, timedelta

def medir_tiempo(func):
    """Decorador para medir tiempo de ejecución"""
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        tiempo = time.time() - inicio
        return resultado, tiempo
    return wrapper

class PerformanceTester:
    def __init__(self):
        self.db = Database()
    
    @medir_tiempo
    def test_busqueda_paciente_sin_indice(self, paciente_id):
        """Buscar paciente SIN usar índice"""
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM pacientes 
                    WHERE id = %s
                """, (paciente_id,))
                return cursor.fetchone()
        finally:
            self.db.release_connection(conn)
    
    @medir_tiempo
    def test_busqueda_ordenes_paciente(self, paciente_id):
        """REQUISITO 2: Buscar órdenes de un paciente (con índice)"""
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT o.*, COUNT(r.id) as total_analisis
                    FROM ordenes o
                    LEFT JOIN resultados r ON o.id = r.orden_id
                    WHERE o.paciente_id = %s
                    GROUP BY o.id
                    ORDER BY o.fecha_orden DESC
                """, (paciente_id,))
                return cursor.fetchall()
        finally:
            self.db.release_connection(conn)
    
    @medir_tiempo
    def test_estadisticas_periodo(self, dias=30):
        """REQUISITO 6: Estadísticas optimizadas por período"""
        conn = self.db.get_connection()
        try:
            fecha_fin = datetime.now()
            fecha_inicio = fecha_fin - timedelta(days=dias)
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ta.nombre,
                        COUNT(*) as total,
                        ROUND(AVG(r.valor), 2) as promedio,
                        MIN(r.valor) as minimo,
                        MAX(r.valor) as maximo,
                        SUM(CASE WHEN r.fuera_rango = TRUE THEN 1 ELSE 0 END) as fuera_rango
                    FROM resultados r
                    JOIN tipos_analisis ta ON r.tipo_analisis_id = ta.id
                    WHERE r.fecha_resultado BETWEEN %s AND %s
                    AND r.valor IS NOT NULL
                    GROUP BY ta.id, ta.nombre
                    ORDER BY total DESC
                """, (fecha_inicio, fecha_fin))
                return cursor.fetchall()
        finally:
            self.db.release_connection(conn)
    
    @medir_tiempo
    def test_auditoria_resultado(self, resultado_id):
        """REQUISITO 4: Consultar auditoría con índices"""
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT fecha, accion, usuario, detalles
                    FROM auditoria_accesos
                    WHERE tabla = 'resultados' AND registro_id = %s
                    ORDER BY fecha DESC
                """, (resultado_id,))
                return cursor.fetchall()
        finally:
            self.db.release_connection(conn)
    
    @medir_tiempo
    def test_ordenes_pendientes(self):
        """Consultar órdenes pendientes (índice en estado)"""
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT o.id, o.paciente_id, o.fecha_orden,
                           COUNT(r.id) as total_analisis,
                           SUM(CASE WHEN r.valor IS NULL THEN 1 ELSE 0 END) as pendientes
                    FROM ordenes o
                    JOIN resultados r ON o.id = r.orden_id
                    WHERE o.estado = 'PENDIENTE'
                    GROUP BY o.id, o.paciente_id, o.fecha_orden
                    HAVING SUM(CASE WHEN r.valor IS NULL THEN 1 ELSE 0 END) > 0
                    ORDER BY o.fecha_orden DESC
                    LIMIT 100
                """)
                return cursor.fetchall()
        finally:
            self.db.release_connection(conn)
    
    @medir_tiempo
    def test_top_pacientes_analisis(self, limite=100):
        """Top pacientes con más análisis realizados"""
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.id, COUNT(r.id) as total_analisis,
                           COUNT(DISTINCT o.id) as total_ordenes
                    FROM pacientes p
                    JOIN ordenes o ON p.id = o.paciente_id
                    JOIN resultados r ON o.id = r.orden_id
                    WHERE r.valor IS NOT NULL
                    GROUP BY p.id
                    ORDER BY total_analisis DESC
                    LIMIT %s
                """, (limite,))
                return cursor.fetchall()
        finally:
            self.db.release_connection(conn)
    
    def ejecutar_todos_los_tests(self):
        """Ejecutar batería completa de tests"""
        print("\n" + "="*80)
        print("TEST DE RENDIMIENTO Y OPTIMIZACIÓN")
        print("="*80)
        
        # Test 1: Búsqueda de paciente
        print("\nTest 1: Búsqueda de paciente por ID")
        resultado, tiempo = self.test_busqueda_paciente_sin_indice(100)
        print(f"   Tiempo: {tiempo*1000:.2f} ms")
        print(f"   ✓ {'Encontrado' if resultado else 'No encontrado'}")
        
        # Test 2: Órdenes de un paciente
        print("\nTest 2: Órdenes de un paciente (con índice)")
        resultado, tiempo = self.test_busqueda_ordenes_paciente(100)
        print(f"   Tiempo: {tiempo*1000:.2f} ms")
        print(f"   ✓ Órdenes encontradas: {len(resultado)}")
        
        # Test 3: Estadísticas por período
        print("\nTest 3: Estadísticas de últimos 30 días (REQUISITO 6)")
        resultado, tiempo = self.test_estadisticas_periodo(30)
        print(f"   Tiempo: {tiempo*1000:.2f} ms")
        print(f"   ✓ Tipos de análisis: {len(resultado)}")
        if resultado:
            print(f"   ✓ Análisis más común: {resultado[0][0]} ({resultado[0][1]} veces)")
        
        # Test 4: Auditoría
        print("\nTest 4: Consultar auditoría (REQUISITO 4)")
        resultado, tiempo = self.test_auditoria_resultado(1000)
        print(f"   Tiempo: {tiempo*1000:.2f} ms")
        print(f"   ✓ Registros de auditoría: {len(resultado)}")
        
        # Test 5: Órdenes pendientes
        print("\nTest 5: Órdenes pendientes (índice en estado)")
        resultado, tiempo = self.test_ordenes_pendientes()
        print(f"   Tiempo: {tiempo*1000:.2f} ms")
        print(f"   ✓ Órdenes pendientes: {len(resultado)}")
        
        # Test 6: Top pacientes
        print("\nTest 6: Top 100 pacientes con más análisis")
        resultado, tiempo = self.test_top_pacientes_analisis(100)
        print(f"   Tiempo: {tiempo*1000:.2f} ms")
        print(f"   ✓ Pacientes analizados: {len(resultado)}")
        if resultado:
            print(f"   ✓ Paciente con más análisis: ID {resultado[0][0]} ({resultado[0][1]} análisis)")
        
    print("\n" + "="*80)
    print("TESTS DE RENDIMIENTO COMPLETADOS")
    print("="*80)

def analizar_indices(self):
    """Analizar el uso de índices en las tablas"""
    print("\nANÁLISIS DE ÍNDICES")
    print("-"*80)
    
    conn = self.db.get_connection()
    try:
        with conn.cursor() as cursor:
            # Listar todos los índices
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    pg_size_pretty(pg_relation_size(indexname::regclass)) as index_size
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """)
            
            indices = cursor.fetchall()
            
            tabla_actual = None
            for schema, tabla, indice, tamaño in indices:
                if tabla != tabla_actual:
                    print(f"\nTabla: {tabla}")
                    tabla_actual = tabla
                print(f"   ├─ {indice}: {tamaño}")
            
            # Tamaño total de índices
            cursor.execute("""
                SELECT pg_size_pretty(SUM(pg_relation_size(indexname::regclass)))
                FROM pg_indexes
                WHERE schemaname = 'public'
            """)
            
            tamaño_total = cursor.fetchone()[0]
            print(f"\nTamaño total de índices: {tamaño_total}")
            
    finally:
        self.db.release_connection(conn)


if __name__ == '__main__':
    tester = PerformanceTester()
    tester.ejecutar_todos_los_tests()