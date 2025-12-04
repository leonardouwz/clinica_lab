import psycopg2
from datetime import datetime
from database import Database
from auditoria import registrar_auditoria

db = Database()

# REQUISITO 1: Implementar transacciones para registro de órdenes
def registrar_orden_con_analisis(paciente_id, lista_analisis_ids, usuario):
    """
    Transacción ACID para registrar una orden con múltiples análisis
    Retorna también los IDs de los resultados creados
    """
    conn = db.get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                # Iniciar transacción explícita
                cursor.execute("BEGIN")
                
                # 1. Crear la orden
                cursor.execute("""
                    INSERT INTO ordenes (paciente_id, usuario_crea)
                    VALUES (%s, %s)
                    RETURNING id
                """, (paciente_id, usuario))
                
                orden_id = cursor.fetchone()[0]
                
                # 2. Insertar todos los análisis solicitados y guardar IDs
                ids_resultados = []
                for analisis_id in lista_analisis_ids:
                    cursor.execute("""
                        INSERT INTO resultados 
                        (orden_id, tipo_analisis_id, usuario_carga)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (orden_id, analisis_id, usuario))
                    
                    resultado_id = cursor.fetchone()[0]
                    ids_resultados.append(resultado_id)
                
                # REQUISITO 4: Registrar en auditoría
                registrar_auditoria(
                    cursor, 'ordenes', orden_id, 'CREATE', 
                    usuario, f'Orden con {len(lista_analisis_ids)} análisis'
                )
                
                # Commit de la transacción
                cursor.execute("COMMIT")
                
                return orden_id, "Orden registrada exitosamente", ids_resultados
                
    except Exception as e:
        conn.rollback()
        return None, f"Error en transacción: {str(e)}", []
    
    finally:
        db.release_connection(conn)


# REQUISITO 1: Implementar transacciones para carga de resultados
def cargar_resultado_con_validacion(resultado_id, valor, usuario, ip_address=None):
    """
    Transacción ACID para cargar resultado con validación de rango
    """
    conn = db.get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("BEGIN")
                
                # Obtener rango normal del tipo de análisis
                cursor.execute("""
                    SELECT ta.valor_min, ta.valor_max, ta.nombre
                    FROM resultados r
                    JOIN tipos_analisis ta ON r.tipo_analisis_id = ta.id
                    WHERE r.id = %s
                """, (resultado_id,))
                
                rango = cursor.fetchone()
                if not rango:
                    raise Exception("Resultado no encontrado")
                
                valor_min, valor_max, nombre_analisis = rango
                
                # REQUISITO 5: Validación transaccional de rangos normales
                fuera_rango = False
                if valor_min is not None and valor_max is not None:
                    if valor < valor_min or valor > valor_max:
                        fuera_rango = True
                
                # Actualizar resultado
                cursor.execute("""
                    UPDATE resultados
                    SET valor = %s,
                        fecha_resultado = %s,
                        fuera_rango = %s,
                        usuario_carga = %s
                    WHERE id = %s
                """, (valor, datetime.now(), fuera_rango, usuario, resultado_id))
                
                # Actualizar estado de la orden si todos los resultados están completos
                cursor.execute("""
                    UPDATE ordenes
                    SET estado = 'COMPLETADO'
                    WHERE id = (SELECT orden_id FROM resultados WHERE id = %s)
                    AND NOT EXISTS (
                        SELECT 1 FROM resultados 
                        WHERE orden_id = ordenes.id AND valor IS NULL
                    )
                """, (resultado_id,))
                
                # REQUISITO 4: Auditoría de acceso
                registrar_auditoria(
                    cursor, 'resultados', resultado_id, 'UPDATE',
                    usuario, f'{nombre_analisis}: {valor} {"[FUERA DE RANGO]" if fuera_rango else ""}',
                    ip_address
                )
                
                cursor.execute("COMMIT")
                
                return True, fuera_rango, "Resultado cargado exitosamente"
                
    except Exception as e:
        conn.rollback()
        return False, False, f"Error: {str(e)}"
    
    finally:
        db.release_connection(conn)


def registrar_paciente(nombre, dni, fecha_nac, telefono, usuario):
    """
    Transacción para registrar paciente con datos encriptados
    """
    conn = db.get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("BEGIN")
                
                # REQUISITO 3: Encriptar datos sensibles
                nombre_enc = db.encriptar(nombre)
                dni_enc = db.encriptar(dni)
                telefono_enc = db.encriptar(telefono) if telefono else None
                
                cursor.execute("""
                    INSERT INTO pacientes 
                    (nombre_enc, dni_enc, fecha_nacimiento, telefono_enc)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (nombre_enc, dni_enc, fecha_nac, telefono_enc))
                
                paciente_id = cursor.fetchone()[0]
                
                registrar_auditoria(
                    cursor, 'pacientes', paciente_id, 'CREATE',
                    usuario, f'Nuevo paciente registrado'
                )
                
                cursor.execute("COMMIT")
                return paciente_id, "Paciente registrado"
                
    except psycopg2.IntegrityError:
        conn.rollback()
        return None, "DNI ya existe en el sistema"
    except Exception as e:
        conn.rollback()
        return None, f"Error: {str(e)}"
    finally:
        db.release_connection(conn)