"""
Script para inserción masiva de datos de prueba
Genera miles de registros para testing de optimización
"""

import psycopg2
from datetime import datetime, timedelta
import random
from database import Database
from config import DB_CONFIG

# Nombres y apellidos para generar datos aleatorios
NOMBRES = [
    "Juan", "María", "Carlos", "Ana", "Luis", "Carmen", "José", "Isabel",
    "Francisco", "Laura", "Antonio", "Mercedes", "Manuel", "Rosa", "Pedro",
    "Dolores", "Javier", "Pilar", "Miguel", "Teresa", "Rafael", "Lucía",
    "Ángel", "Josefa", "Fernando", "Francisca", "Alejandro", "Antonia",
    "Ricardo", "Cristina", "Alberto", "Marta", "Eduardo", "Silvia", "Roberto"
]

APELLIDOS = [
    "García", "Rodríguez", "Martínez", "López", "González", "Pérez", "Sánchez",
    "Ramírez", "Torres", "Flores", "Rivera", "Gómez", "Díaz", "Cruz", "Morales",
    "Reyes", "Gutiérrez", "Ortiz", "Chávez", "Ruiz", "Jiménez", "Hernández",
    "Mendoza", "Castillo", "Vargas", "Romero", "Álvarez", "Medina", "Rojas"
]

def generar_nombre_completo():
    """Genera un nombre completo aleatorio"""
    nombre = random.choice(NOMBRES)
    apellido1 = random.choice(APELLIDOS)
    apellido2 = random.choice(APELLIDOS)
    return f"{nombre} {apellido1} {apellido2}"

def generar_dni():
    """Genera un DNI aleatorio"""
    return f"{random.randint(10000000, 99999999)}"

def generar_telefono():
    """Genera un teléfono aleatorio"""
    return f"+51{random.randint(900000000, 999999999)}"

def generar_fecha_nacimiento():
    """Genera una fecha de nacimiento aleatoria (18-90 años)"""
    años_atras = random.randint(18, 90)
    fecha = datetime.now() - timedelta(days=años_atras*365 + random.randint(0, 365))
    return fecha.date()

class MassiveDataInserter:
    def __init__(self):
        self.db = Database()
        self.conn = None
        self.cursor = None
        
    def conectar(self):
        """Establecer conexión directa sin pool"""
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()
        print("✓ Conexión establecida")
    
    def desconectar(self):
        """Cerrar conexión"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✓ Conexión cerrada")
    
    def limpiar_datos(self):
        """Limpiar todos los datos de las tablas (CUIDADO!)"""
        print("\n⚠️  LIMPIANDO DATOS EXISTENTES...")
        try:
            self.cursor.execute("TRUNCATE TABLE auditoria_accesos RESTART IDENTITY CASCADE;")
            self.cursor.execute("TRUNCATE TABLE resultados RESTART IDENTITY CASCADE;")
            self.cursor.execute("TRUNCATE TABLE ordenes RESTART IDENTITY CASCADE;")
            self.cursor.execute("TRUNCATE TABLE pacientes RESTART IDENTITY CASCADE;")
            self.conn.commit()
            print("✓ Datos limpiados")
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error limpiando datos: {e}")
    
    def insertar_pacientes(self, cantidad=10000):
        """
        Insertar pacientes masivamente con encriptación
        """
        print(f"\n📋 INSERTANDO {cantidad} PACIENTES...")
        print("Esto puede tomar varios minutos debido a la encriptación...")
        
        inicio = datetime.now()
        insertados = 0
        errores = 0
        
        # Usar transacciones por lotes de 100
        lote_size = 100
        
        for i in range(0, cantidad, lote_size):
            try:
                self.cursor.execute("BEGIN")
                
                lote_actual = min(lote_size, cantidad - i)
                
                for j in range(lote_actual):
                    nombre = generar_nombre_completo()
                    dni = generar_dni()
                    fecha_nac = generar_fecha_nacimiento()
                    telefono = generar_telefono()
                    
                    # Encriptar datos sensibles
                    nombre_enc = self.db.encriptar(nombre)
                    dni_enc = self.db.encriptar(dni)
                    tel_enc = self.db.encriptar(telefono)
                    
                    try:
                        self.cursor.execute("""
                            INSERT INTO pacientes (nombre_enc, dni_enc, fecha_nacimiento, telefono_enc, created_at)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (nombre_enc, dni_enc, fecha_nac, tel_enc, 
                              datetime.now() - timedelta(days=random.randint(0, 730))))
                        
                        insertados += 1
                        
                    except psycopg2.IntegrityError:
                        # DNI duplicado, continuar
                        errores += 1
                        continue
                
                self.cursor.execute("COMMIT")
                
                # Progreso
                if (i + lote_actual) % 1000 == 0:
                    print(f"  Progreso: {i + lote_actual}/{cantidad} pacientes ({insertados} insertados, {errores} duplicados)")
                    
            except Exception as e:
                self.cursor.execute("ROLLBACK")
                print(f"❌ Error en lote {i}-{i+lote_actual}: {e}")
                errores += lote_actual
        
        tiempo = (datetime.now() - inicio).total_seconds()
        print(f"✓ Pacientes insertados: {insertados}")
        print(f"  Duplicados/errores: {errores}")
        print(f"  Tiempo total: {tiempo:.2f} segundos")
        print(f"  Velocidad: {insertados/tiempo:.2f} registros/segundo")
        
        return insertados
    
    def insertar_ordenes_masivas(self, cantidad=50000):
        """
        Insertar órdenes con múltiples análisis
        """
        print(f"\n🧪 INSERTANDO {cantidad} ÓRDENES...")
        
        # Obtener IDs de pacientes
        self.cursor.execute("SELECT id FROM pacientes")
        pacientes_ids = [row[0] for row in self.cursor.fetchall()]
        
        if not pacientes_ids:
            print("❌ No hay pacientes. Inserta pacientes primero.")
            return 0
        
        print(f"  Pacientes disponibles: {len(pacientes_ids)}")
        
        # IDs de tipos de análisis (1-5)
        tipos_analisis = [1, 2, 3, 4, 5]
        usuarios = ["admin", "doctor1", "doctor2", "laboratorista1", "laboratorista2"]
        estados = ["PENDIENTE", "COMPLETADO"]
        
        inicio = datetime.now()
        insertados = 0
        
        lote_size = 500
        
        for i in range(0, cantidad, lote_size):
            try:
                self.cursor.execute("BEGIN")
                
                lote_actual = min(lote_size, cantidad - i)
                
                for j in range(lote_actual):
                    paciente_id = random.choice(pacientes_ids)
                    usuario = random.choice(usuarios)
                    
                    # Fecha de orden entre últimos 365 días
                    fecha_orden = datetime.now() - timedelta(days=random.randint(0, 365))
                    
                    # Estado: 80% completado, 20% pendiente
                    estado = random.choices(estados, weights=[20, 80])[0]
                    
                    # Insertar orden
                    self.cursor.execute("""
                        INSERT INTO ordenes (paciente_id, fecha_orden, estado, usuario_crea)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """, (paciente_id, fecha_orden, estado, usuario))
                    
                    orden_id = self.cursor.fetchone()[0]
                    
                    # Insertar 1-5 análisis por orden
                    num_analisis = random.randint(1, 5)
                    analisis_seleccionados = random.sample(tipos_analisis, num_analisis)
                    
                    for tipo_id in analisis_seleccionados:
                        self.cursor.execute("""
                            INSERT INTO resultados (orden_id, tipo_analisis_id, usuario_carga)
                            VALUES (%s, %s, %s)
                        """, (orden_id, tipo_id, usuario))
                    
                    insertados += 1
                
                self.cursor.execute("COMMIT")
                
                if (i + lote_actual) % 5000 == 0:
                    print(f"  Progreso: {i + lote_actual}/{cantidad} órdenes")
                    
            except Exception as e:
                self.cursor.execute("ROLLBACK")
                print(f"❌ Error en lote {i}: {e}")
        
        tiempo = (datetime.now() - inicio).total_seconds()
        print(f"✓ Órdenes insertadas: {insertados}")
        print(f"  Tiempo total: {tiempo:.2f} segundos")
        print(f"  Velocidad: {insertados/tiempo:.2f} órdenes/segundo")
        
        return insertados
    
    def cargar_resultados_masivos(self, porcentaje_completado=80):
        """
        Cargar valores de resultados aleatorios
        """
        print(f"\n📊 CARGANDO RESULTADOS ({porcentaje_completado}% de completitud)...")
        
        # Obtener resultados sin valor
        self.cursor.execute("SELECT COUNT(*) FROM resultados WHERE valor IS NULL")
        total_pendientes = self.cursor.fetchone()[0]
        
        cantidad_a_completar = int(total_pendientes * porcentaje_completado / 100)
        
        print(f"  Resultados pendientes: {total_pendientes}")
        print(f"  Se completarán: {cantidad_a_completar}")
        
        # Obtener rangos normales
        self.cursor.execute("SELECT id, valor_min, valor_max FROM tipos_analisis")
        rangos = {row[0]: (row[1], row[2]) for row in self.cursor.fetchall()}
        
        inicio = datetime.now()
        completados = 0
        fuera_rango = 0
        
        # Obtener IDs de resultados pendientes
        self.cursor.execute("""
            SELECT id, tipo_analisis_id 
            FROM resultados 
            WHERE valor IS NULL 
            LIMIT %s
        """, (cantidad_a_completar,))
        
        resultados_pendientes = self.cursor.fetchall()
        
        usuarios = ["laboratorista1", "laboratorista2", "laboratorista3"]
        
        lote_size = 1000
        
        for i in range(0, len(resultados_pendientes), lote_size):
            try:
                self.cursor.execute("BEGIN")
                
                lote = resultados_pendientes[i:i+lote_size]
                
                for resultado_id, tipo_id in lote:
                    valor_min, valor_max = rangos.get(tipo_id, (0, 100))
                    
                    # 85% dentro del rango, 15% fuera
                    if random.random() < 0.85:
                        # Dentro del rango
                        valor = round(random.uniform(float(valor_min), float(valor_max)), 2)
                        es_fuera_rango = False
                    else:
                        # Fuera del rango
                        if random.random() < 0.5:
                            # Por debajo
                            valor = round(random.uniform(float(valor_min) * 0.5, float(valor_min)), 2)
                        else:
                            # Por encima
                            valor = round(random.uniform(float(valor_max), float(valor_max) * 1.5), 2)
                        es_fuera_rango = True
                        fuera_rango += 1
                    
                    fecha_resultado = datetime.now() - timedelta(days=random.randint(0, 300))
                    usuario = random.choice(usuarios)
                    
                    # REQUISITO 5: Validación de rango
                    self.cursor.execute("""
                        UPDATE resultados
                        SET valor = %s,
                            fecha_resultado = %s,
                            usuario_carga = %s,
                            fuera_rango = %s
                        WHERE id = %s
                    """, (valor, fecha_resultado, usuario, es_fuera_rango, resultado_id))
                    
                    # REQUISITO 4: Auditoría
                    self.cursor.execute("""
                        INSERT INTO auditoria_accesos 
                        (tabla, registro_id, accion, usuario, detalles, fecha)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, ('resultados', resultado_id, 'UPDATE', usuario, 
                          f'Valor: {valor}', fecha_resultado))
                    
                    completados += 1
                
                self.cursor.execute("COMMIT")
                
                if (i + len(lote)) % 5000 == 0:
                    print(f"  Progreso: {i + len(lote)}/{len(resultados_pendientes)} resultados")
                    
            except Exception as e:
                self.cursor.execute("ROLLBACK")
                print(f"❌ Error en lote {i}: {e}")
        
        # Actualizar estados de órdenes
        print("  Actualizando estados de órdenes...")
        self.cursor.execute("""
            UPDATE ordenes
            SET estado = 'COMPLETADO'
            WHERE id IN (
                SELECT orden_id 
                FROM resultados 
                WHERE valor IS NOT NULL
                GROUP BY orden_id
                HAVING COUNT(*) = (
                    SELECT COUNT(*) 
                    FROM resultados r2 
                    WHERE r2.orden_id = resultados.orden_id
                )
            )
        """)
        self.conn.commit()
        
        tiempo = (datetime.now() - inicio).total_seconds()
        print(f"✓ Resultados cargados: {completados}")
        print(f"  Fuera de rango: {fuera_rango} ({fuera_rango*100/completados:.1f}%)")
        print(f"  Tiempo total: {tiempo:.2f} segundos")
        print(f"  Velocidad: {completados/tiempo:.2f} resultados/segundo")
    
    def generar_estadisticas(self):
        """Mostrar estadísticas de los datos insertados"""
        print("\n" + "="*70)
        print("📈 ESTADÍSTICAS DE DATOS GENERADOS")
        print("="*70)
        
        # Contar pacientes
        self.cursor.execute("SELECT COUNT(*) FROM pacientes")
        total_pacientes = self.cursor.fetchone()[0]
        print(f"\n👥 Pacientes: {total_pacientes:,}")
        
        # Contar órdenes
        self.cursor.execute("SELECT COUNT(*) FROM ordenes")
        total_ordenes = self.cursor.fetchone()[0]
        print(f"📋 Órdenes: {total_ordenes:,}")
        
        # Órdenes por estado
        self.cursor.execute("""
            SELECT estado, COUNT(*) 
            FROM ordenes 
            GROUP BY estado
        """)
        for estado, count in self.cursor.fetchall():
            print(f"   - {estado}: {count:,}")
        
        # Contar resultados
        self.cursor.execute("SELECT COUNT(*) FROM resultados")
        total_resultados = self.cursor.fetchone()[0]
        print(f"\n🧪 Resultados totales: {total_resultados:,}")
        
        # Resultados completados vs pendientes
        self.cursor.execute("SELECT COUNT(*) FROM resultados WHERE valor IS NOT NULL")
        completados = self.cursor.fetchone()[0]
        pendientes = total_resultados - completados
        print(f"   - Completados: {completados:,} ({completados*100/total_resultados:.1f}%)")
        print(f"   - Pendientes: {pendientes:,} ({pendientes*100/total_resultados:.1f}%)")
        
        # Fuera de rango
        self.cursor.execute("SELECT COUNT(*) FROM resultados WHERE fuera_rango = TRUE")
        fuera_rango = self.cursor.fetchone()[0]
        if completados > 0:
            print(f"   - Fuera de rango: {fuera_rango:,} ({fuera_rango*100/completados:.1f}%)")
        
        # Auditoría
        self.cursor.execute("SELECT COUNT(*) FROM auditoria_accesos")
        total_auditoria = self.cursor.fetchone()[0]
        print(f"\n🔍 Registros de auditoría: {total_auditoria:,}")
        
        # Distribución por tipo de análisis
        print(f"\n📊 Distribución por tipo de análisis:")
        self.cursor.execute("""
            SELECT ta.codigo, ta.nombre, COUNT(r.id) as total,
                   SUM(CASE WHEN r.valor IS NOT NULL THEN 1 ELSE 0 END) as completados
            FROM tipos_analisis ta
            LEFT JOIN resultados r ON ta.id = r.tipo_analisis_id
            GROUP BY ta.id, ta.codigo, ta.nombre
            ORDER BY total DESC
        """)
        for codigo, nombre, total, comp in self.cursor.fetchall():
            print(f"   {codigo} - {nombre}: {total:,} ({comp:,} completados)")
        
        # Tamaño de la base de datos
        self.cursor.execute("""
            SELECT 
                pg_size_pretty(pg_database_size(current_database())) as db_size
        """)
        db_size = self.cursor.fetchone()[0]
        print(f"\n💾 Tamaño de la base de datos: {db_size}")
        
        print("="*70)

def menu_principal():
    """Menú interactivo para inserción de datos"""
    inserter = MassiveDataInserter()
    
    print("\n" + "="*70)
    print("🏥 SISTEMA DE INSERCIÓN MASIVA DE DATOS - ClinicalLabManager")
    print("="*70)
    
    inserter.conectar()
    
    while True:
        print("\n" + "-"*70)
        print("OPCIONES:")
        print("-"*70)
        print("1. Insertar pacientes")
        print("2. Insertar órdenes")
        print("3. Cargar resultados")
        print("4. Proceso completo (Pacientes + Órdenes + Resultados)")
        print("5. Ver estadísticas")
        print("6. Limpiar todos los datos (⚠️ PELIGRO)")
        print("0. Salir")
        print("-"*70)
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            cantidad = input("¿Cuántos pacientes? (default: 10000): ").strip()
            cantidad = int(cantidad) if cantidad else 10000
            inserter.insertar_pacientes(cantidad)
            
        elif opcion == "2":
            cantidad = input("¿Cuántas órdenes? (default: 50000): ").strip()
            cantidad = int(cantidad) if cantidad else 50000
            inserter.insertar_ordenes_masivas(cantidad)
            
        elif opcion == "3":
            porcentaje = input("¿Qué % completar? (default: 80): ").strip()
            porcentaje = int(porcentaje) if porcentaje else 80
            inserter.cargar_resultados_masivos(porcentaje)
            
        elif opcion == "4":
            print("\n🚀 PROCESO COMPLETO DE INSERCIÓN")
            print("Este proceso insertará:")
            print("  - 10,000 pacientes")
            print("  - 50,000 órdenes")
            print("  - ~150,000 resultados (80% completados)")
            print("\nEsto puede tomar 10-30 minutos dependiendo de tu hardware.")
            
            confirmar = input("\n¿Continuar? (s/n): ").strip().lower()
            if confirmar == 's':
                inicio_total = datetime.now()
                
                inserter.insertar_pacientes(10000)
                inserter.insertar_ordenes_masivas(50000)
                inserter.cargar_resultados_masivos(80)
                inserter.generar_estadisticas()
                
                tiempo_total = (datetime.now() - inicio_total).total_seconds()
                print(f"\n✅ PROCESO COMPLETO FINALIZADO")
                print(f"⏱️  Tiempo total: {tiempo_total/60:.2f} minutos")
            
        elif opcion == "5":
            inserter.generar_estadisticas()
            
        elif opcion == "6":
            print("\n⚠️  ADVERTENCIA: Esto eliminará TODOS los datos")
            confirmar = input("Escriba 'CONFIRMAR' para continuar: ").strip()
            if confirmar == "CONFIRMAR":
                inserter.limpiar_datos()
            else:
                print("❌ Operación cancelada")
                
        elif opcion == "0":
            print("\n👋 Saliendo...")
            break
            
        else:
            print("❌ Opción inválida")
    
    inserter.desconectar()

if __name__ == '__main__':
    menu_principal()