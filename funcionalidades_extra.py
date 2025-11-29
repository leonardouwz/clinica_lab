"""
Funcionalidades adicionales para mayor flexibilidad del sistema
"""

from database import Database
from datetime import datetime, timedelta
import csv

class FuncionalidadesExtra:
    def __init__(self):
        self.db = Database()
    
    # ========== GESTIÓN DE TIPOS DE ANÁLISIS ==========
    
    def agregar_tipo_analisis(self, codigo, nombre, valor_min, valor_max, unidad):
        """
        Permite agregar nuevos tipos de análisis dinámicamente
        """
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO tipos_analisis (codigo, nombre, valor_min, valor_max, unidad)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (codigo, nombre, valor_min, valor_max, unidad))
                
                nuevo_id = cursor.fetchone()[0]
                conn.commit()
                return nuevo_id, "Tipo de análisis agregado exitosamente"
        except Exception as e:
            conn.rollback()
            return None, f"Error: {str(e)}"
        finally:
            self.db.release_connection(conn)
    
    def modificar_rangos_analisis(self, tipo_id, nuevo_min, nuevo_max):
        """
        Modificar rangos normales de un tipo de análisis
        """
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE tipos_analisis
                    SET valor_min = %s, valor_max = %s
                    WHERE id = %s
                """, (nuevo_min, nuevo_max, tipo_id))
                
                conn.commit()
                return True, "Rangos actualizados exitosamente"
        except Exception as e:
            conn.rollback()
            return False, f"Error: {str(e)}"
        finally:
            self.db.release_connection(conn)
    
    def listar_tipos_analisis(self):
        """
        Listar todos los tipos de análisis disponibles
        """
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, codigo, nombre, valor_min, valor_max, unidad
                    FROM tipos_analisis
                    ORDER BY nombre
                """)
                return cursor.fetchall()
        finally:
            self.db.release_connection(conn)
    
    # ========== BÚSQUEDAS AVANZADAS ==========
    
    def buscar_paciente_por_dni(self, dni):
        """
        Buscar paciente por DNI (requiere desencriptar)
        """
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, nombre_enc, dni_enc, fecha_nacimiento, telefono_enc
                    FROM pacientes
                """)
                
                pacientes = cursor.fetchall()
                
                # Buscar desencriptando
                for pac in pacientes:
                    dni_desenc = self.db.desencriptar(pac[2])
                    if dni_desenc == dni:
                        return {
                            'id': pac[0],
                            'nombre': self.db.desencriptar(pac[1]),
                            'dni': dni_desenc,
                            'fecha_nacimiento': pac[3],
                            'telefono': self.db.desencriptar(pac[4]) if pac[4] else None
                        }
                
                return None
        finally:
            self.db.release_connection(conn)
    
    def buscar_paciente_por_nombre(self, nombre_parcial):
        """
        Buscar pacientes por nombre (búsqueda parcial)
        """
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, nombre_enc, dni_enc
                    FROM pacientes
                """)
                
                pacientes = cursor.fetchall()
                resultados = []
                
                nombre_parcial = nombre_parcial.lower()
                
                for pac in pacientes:
                    nombre_desenc = self.db.desencriptar(pac[1]).lower()
                    if nombre_parcial in nombre_desenc:
                        resultados.append({
                            'id': pac[0],
                            'nombre': self.db.desencriptar(pac[1]),
                            'dni': self.db.desencriptar(pac[2])
                        })
                
                return resultados
        finally:
            self.db.release_connection(conn)
    
    def obtener_historial_paciente(self, paciente_id):
        """
        Obtener historial completo de análisis de un paciente
        """
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        o.id as orden_id,
                        o.fecha_orden,
                        o.estado,
                        ta.nombre as analisis,
                        r.valor,
                        r.fecha_resultado,
                        r.fuera_rango,
                        ta.valor_min,
                        ta.valor_max,
                        ta.unidad
                    FROM ordenes o
                    JOIN resultados r ON o.id = r.orden_id
                    JOIN tipos_analisis ta ON r.tipo_analisis_id = ta.id
                    WHERE o.paciente_id = %s
                    ORDER BY o.fecha_orden DESC, ta.nombre
                """, (paciente_id,))
                
                return cursor.fetchall()
        finally:
            self.db.release_connection(conn)
    
    # ========== REPORTES Y EXPORTACIÓN ==========
    
    def exportar_resultados_csv(self, orden_id, archivo='resultados.csv'):
        """
        Exportar resultados de una orden a CSV
        """
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ta.codigo,
                        ta.nombre,
                        r.valor,
                        ta.valor_min,
                        ta.valor_max,
                        ta.unidad,
                        r.fecha_resultado,
                        r.fuera_rango
                    FROM resultados r
                    JOIN tipos_analisis ta ON r.tipo_analisis_id = ta.id
                    WHERE r.orden_id = %s AND r.valor IS NOT NULL
                    ORDER BY ta.nombre
                """, (orden_id,))
                
                resultados = cursor.fetchall()
                
                with open(archivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Código', 'Análisis', 'Valor', 'Min', 'Max', 
                                   'Unidad', 'Fecha', 'Fuera Rango'])
                    writer.writerows(resultados)
                
                return True, f"Resultados exportados a {archivo}"
        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            self.db.release_connection(conn)
    
    def generar_reporte_paciente(self, paciente_id, archivo='reporte_paciente.txt'):
        """
        Generar reporte completo de un paciente
        """
        conn = self.db.get_connection()
        try:
            # Datos del paciente
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT nombre_enc, dni_enc, fecha_nacimiento, telefono_enc, created_at
                    FROM pacientes WHERE id = %s
                """, (paciente_id,))
                
                pac = cursor.fetchone()
                if not pac:
                    return False, "Paciente no encontrado"
                
                nombre = self.db.desencriptar(pac[0])
                dni = self.db.desencriptar(pac[1])
                fecha_nac = pac[2]
                telefono = self.db.desencriptar(pac[3]) if pac[3] else "N/A"
                created = pac[4]
            
            # Historial
            historial = self.obtener_historial_paciente(paciente_id)
            
            # Generar reporte
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write("="*70 + "\n")
                f.write("REPORTE MÉDICO - HISTORIAL DE ANÁLISIS CLÍNICOS\n")
                f.write("="*70 + "\n\n")
                
                f.write(f"DATOS DEL PACIENTE\n")
                f.write("-"*70 + "\n")
                f.write(f"ID: {paciente_id}\n")
                f.write(f"Nombre: {nombre}\n")
                f.write(f"DNI: {dni}\n")
                f.write(f"Fecha Nacimiento: {fecha_nac}\n")
                f.write(f"Teléfono: {telefono}\n")
                f.write(f"Registrado: {created}\n\n")
                
                f.write(f"HISTORIAL DE ANÁLISIS\n")
                f.write("="*70 + "\n\n")
                
                orden_actual = None
                for row in historial:
                    orden_id, fecha_orden, estado, analisis, valor, fecha_res, fuera, vmin, vmax, unidad = row
                    
                    if orden_id != orden_actual:
                        f.write(f"\n{'─'*70}\n")
                        f.write(f"ORDEN #{orden_id} - {fecha_orden} - Estado: {estado}\n")
                        f.write(f"{'─'*70}\n")
                        orden_actual = orden_id
                    
                    alerta = " ⚠️ FUERA DE RANGO" if fuera else ""
                    f.write(f"  • {analisis}: {valor} {unidad} ")
                    f.write(f"(Rango: {vmin}-{vmax}){alerta}\n")
                    if fecha_res:
                        f.write(f"    Fecha resultado: {fecha_res}\n")
                
                f.write("\n" + "="*70 + "\n")
                f.write(f"Reporte generado: {datetime.now()}\n")
            
            return True, f"Reporte generado: {archivo}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            self.db.release_connection(conn)
    
    # ========== GESTIÓN DE USUARIOS Y ROLES ==========
    
    def registrar_usuario(self, username, nombre_completo, rol):
        """
        Sistema básico de usuarios (expandible)
        """
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                # Crear tabla de usuarios si no existe
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        nombre_completo VARCHAR(200) NOT NULL,
                        rol VARCHAR(50) NOT NULL,
                        activo BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    INSERT INTO usuarios (username, nombre_completo, rol)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (username, nombre_completo, rol))
                
                user_id = cursor.fetchone()[0]
                conn.commit()
                
                return user_id, "Usuario registrado exitosamente"
        except Exception as e:
            conn.rollback()
            return None, f"Error: {str(e)}"
        finally:
            self.db.release_connection(conn)
    
    # ========== ALERTAS Y NOTIFICACIONES ==========
    
    def obtener_alertas_urgentes(self):
        """
        Obtener resultados fuera de rango recientes que requieren atención
        """
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        r.id,
                        o.id as orden_id,
                        o.paciente_id,
                        ta.nombre as analisis,
                        r.valor,
                        ta.valor_min,
                        ta.valor_max,
                        ta.unidad,
                        r.fecha_resultado,
                        CASE 
                            WHEN r.valor < ta.valor_min THEN 'BAJO'
                            WHEN r.valor > ta.valor_max THEN 'ALTO'
                        END as tipo_alerta
                    FROM resultados r
                    JOIN ordenes o ON r.orden_id = o.id
                    JOIN tipos_analisis ta ON r.tipo_analisis_id = ta.id
                    WHERE r.fuera_rango = TRUE
                    AND r.fecha_resultado >= NOW() - INTERVAL '7 days'
                    ORDER BY r.fecha_resultado DESC
                    LIMIT 50
                """)
                
                return cursor.fetchall()
        finally:
            self.db.release_connection(conn)
    
    def marcar_alerta_revisada(self, resultado_id, usuario, observaciones):
        """
        Marcar una alerta como revisada
        """
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                # Agregar tabla de alertas revisadas si no existe
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alertas_revisadas (
                        id SERIAL PRIMARY KEY,
                        resultado_id INTEGER REFERENCES resultados(id),
                        usuario VARCHAR(50),
                        observaciones TEXT,
                        fecha_revision TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    INSERT INTO alertas_revisadas (resultado_id, usuario, observaciones)
                    VALUES (%s, %s, %s)
                """, (resultado_id, usuario, observaciones))
                
                conn.commit()
                return True, "Alerta marcada como revisada"
        except Exception as e:
            conn.rollback()
            return False, f"Error: {str(e)}"
        finally:
            self.db.release_connection(conn)
    
    # ========== MODIFICACIÓN Y ELIMINACIÓN ==========
    
    def modificar_paciente(self, paciente_id, nombre=None, telefono=None):
        """
        Modificar datos de un paciente (mantiene encriptación)
        """
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                updates = []
                params = []
                
                if nombre:
                    updates.append("nombre_enc = %s")
                    params.append(self.db.encriptar(nombre))
                
                if telefono:
                    updates.append("telefono_enc = %s")
                    params.append(self.db.encriptar(telefono))
                
                if not updates:
                    return False, "No hay datos para actualizar"
                
                params.append(paciente_id)
                
                query = f"""
                    UPDATE pacientes
                    SET {', '.join(updates)}
                    WHERE id = %s
                """
                
                cursor.execute(query, params)
                conn.commit()
                
                return True, "Paciente actualizado exitosamente"
        except Exception as e:
            conn.rollback()
            return False, f"Error: {str(e)}"
        finally:
            self.db.release_connection(conn)
    
    def cancelar_orden(self, orden_id, usuario, motivo):
        """
        Cancelar una orden (no elimina, marca como cancelada)
        """
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE ordenes
                    SET estado = 'CANCELADO'
                    WHERE id = %s
                """, (orden_id,))
                
                # Registrar en auditoría
                cursor.execute("""
                    INSERT INTO auditoria_accesos 
                    (tabla, registro_id, accion, usuario, detalles)
                    VALUES (%s, %s, %s, %s, %s)
                """, ('ordenes', orden_id, 'CANCEL', usuario, f'Motivo: {motivo}'))
                
                conn.commit()
                return True, "Orden cancelada exitosamente"
        except Exception as e:
            conn.rollback()
            return False, f"Error: {str(e)}"
        finally:
            self.db.release_connection(conn)