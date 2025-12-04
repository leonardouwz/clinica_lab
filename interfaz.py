import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from transacciones import *
from estadisticas import *

class ClinicalLabManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ClinicalLabManager - Sistema de Gestión de Laboratorios")
        self.root.geometry("1000x700")
        
        self.usuario_actual = "admin"  # En producción: sistema de login
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Tabs principales
        notebook = ttk.Notebook(self.root)
        
        # TAB 1: Registrar Pacientes
        tab_pacientes = ttk.Frame(notebook)
        self.crear_tab_pacientes(tab_pacientes)
        notebook.add(tab_pacientes, text="📋 Pacientes")
        
        # TAB 2: Nueva Orden
        tab_ordenes = ttk.Frame(notebook)
        self.crear_tab_ordenes(tab_ordenes)
        notebook.add(tab_ordenes, text="🧪 Nueva Orden")
        
        # TAB 3: Cargar Resultados
        tab_resultados = ttk.Frame(notebook)
        self.crear_tab_resultados(tab_resultados)
        notebook.add(tab_resultados, text="📊 Cargar Resultados")
        
        # TAB 4: Estadísticas
        tab_stats = ttk.Frame(notebook)
        self.crear_tab_estadisticas(tab_stats)
        notebook.add(tab_stats, text="📈 Estadísticas")
        
        # TAB 5: Auditoría
        tab_auditoria = ttk.Frame(notebook)
        self.crear_tab_auditoria(tab_auditoria)
        notebook.add(tab_auditoria, text="🔍 Auditoría")
        
        # TAB 6: Administración
        tab_admin = ttk.Frame(notebook)
        self.crear_tab_administracion(tab_admin)
        notebook.add(tab_admin, text="⚙️ Administración")
        
        notebook.pack(expand=True, fill='both', padx=5, pady=5)
    
    def crear_tab_pacientes(self, parent):
        """TAB 1: Registro de nuevos pacientes"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="REGISTRAR NUEVO PACIENTE", font=('Arial', 14, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=10
        )
        
        # Campos del formulario
        ttk.Label(frame, text="Nombre Completo:").grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.entry_nombre = ttk.Entry(frame, width=40)
        self.entry_nombre.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="DNI:").grid(row=2, column=0, sticky='w', pady=5, padx=5)
        self.entry_dni = ttk.Entry(frame, width=40)
        self.entry_dni.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Fecha Nacimiento (YYYY-MM-DD):").grid(row=3, column=0, sticky='w', pady=5, padx=5)
        self.entry_fecha_nac = ttk.Entry(frame, width=40)
        self.entry_fecha_nac.insert(0, "1990-01-01")
        self.entry_fecha_nac.grid(row=3, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Teléfono:").grid(row=4, column=0, sticky='w', pady=5, padx=5)
        self.entry_telefono = ttk.Entry(frame, width=40)
        self.entry_telefono.grid(row=4, column=1, pady=5, padx=5)
        
        ttk.Button(
            frame, 
            text="Registrar Paciente",
            command=self.registrar_paciente_click
        ).grid(row=5, column=1, pady=20, sticky='e')
        
        # Sección de búsqueda
        ttk.Separator(frame, orient='horizontal').grid(row=6, column=0, columnspan=2, sticky='ew', pady=20)
        
        ttk.Label(frame, text="BUSCAR PACIENTE", font=('Arial', 12, 'bold')).grid(
            row=7, column=0, columnspan=2, pady=10
        )
        
        ttk.Label(frame, text="Buscar por ID:").grid(row=8, column=0, sticky='w', pady=5, padx=5)
        self.entry_buscar_id = ttk.Entry(frame, width=20)
        self.entry_buscar_id.grid(row=8, column=1, pady=5, padx=5, sticky='w')
        
        ttk.Button(
            frame,
            text="Buscar",
            command=self.buscar_paciente
        ).grid(row=9, column=1, pady=5, sticky='w')
        
        # Área de resultados
        self.text_resultado_paciente = tk.Text(frame, height=8, width=70, state='disabled')
        self.text_resultado_paciente.grid(row=10, column=0, columnspan=2, pady=10, padx=5)
    
    def registrar_paciente_click(self):
        """Registrar un nuevo paciente con datos encriptados"""
        try:
            nombre = self.entry_nombre.get().strip()
            dni = self.entry_dni.get().strip()
            fecha_nac = self.entry_fecha_nac.get().strip()
            telefono = self.entry_telefono.get().strip()
            
            if not nombre or not dni:
                messagebox.showwarning("Advertencia", "Nombre y DNI son obligatorios")
                return
            
            # Validar formato de fecha
            try:
                datetime.strptime(fecha_nac, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido (use YYYY-MM-DD)")
                return
            
            # REQUISITO 1 y 3: Transacción con encriptación
            paciente_id, mensaje = registrar_paciente(
                nombre, dni, fecha_nac, telefono, self.usuario_actual
            )
            
            if paciente_id:
                messagebox.showinfo("Éxito", f"Paciente registrado con ID: {paciente_id}\n{mensaje}")
                # Limpiar campos
                self.entry_nombre.delete(0, tk.END)
                self.entry_dni.delete(0, tk.END)
                self.entry_fecha_nac.delete(0, tk.END)
                self.entry_fecha_nac.insert(0, "1990-12-31")
                self.entry_telefono.delete(0, tk.END)
            else:
                messagebox.showerror("Error", mensaje)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    
    def buscar_paciente(self):
        """Buscar y mostrar datos de un paciente"""
        try:
            paciente_id = int(self.entry_buscar_id.get())
            
            from database import Database
            db = Database()
            conn = db.get_connection()
            
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, nombre_enc, dni_enc, fecha_nacimiento, telefono_enc, created_at
                        FROM pacientes
                        WHERE id = %s
                    """, (paciente_id,))
                    
                    resultado = cursor.fetchone()
                    
                    if resultado:
                        # REQUISITO 3: Desencriptar datos sensibles
                        id_pac, nombre_enc, dni_enc, fecha_nac, tel_enc, created = resultado
                        
                        # Convertir memoryview a bytes si es necesario
                        nombre_enc = bytes(nombre_enc) if isinstance(nombre_enc, memoryview) else nombre_enc
                        dni_enc = bytes(dni_enc) if isinstance(dni_enc, memoryview) else dni_enc
                        tel_enc = bytes(tel_enc) if tel_enc and isinstance(tel_enc, memoryview) else tel_enc
                        
                        nombre = db.desencriptar(nombre_enc)
                        dni = db.desencriptar(dni_enc)
                        telefono = db.desencriptar(tel_enc) if tel_enc else "N/A"
                        
                        texto = f"""
    PACIENTE ENCONTRADO
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ID: {id_pac}
    Nombre: {nombre}
    DNI: {dni}
    Fecha de Nacimiento: {fecha_nac}
    Teléfono: {telefono}
    Registrado: {created}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                        """
                        
                        self.text_resultado_paciente.config(state='normal')
                        self.text_resultado_paciente.delete(1.0, tk.END)
                        self.text_resultado_paciente.insert(1.0, texto)
                        self.text_resultado_paciente.config(state='disabled')
                    else:
                        messagebox.showinfo("No encontrado", f"No existe paciente con ID {paciente_id}")
            finally:
                db.release_connection(conn)
                
        except ValueError:
            messagebox.showerror("Error", "ID debe ser un número")
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar: {str(e)}")
    
    def crear_tab_ordenes(self, parent):
        """TAB 2: Crear nuevas órdenes de análisis"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="NUEVA ORDEN DE ANÁLISIS", font=('Arial', 14, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=10
        )
        
        ttk.Label(frame, text="ID del Paciente:").grid(row=1, column=0, sticky='w', pady=5)
        self.entry_paciente_id = ttk.Entry(frame, width=30)
        self.entry_paciente_id.grid(row=1, column=1, pady=5, sticky='w')
        
        ttk.Label(frame, text="Seleccionar Análisis:").grid(row=2, column=0, sticky='nw', pady=5)
        
        # Frame para los checkboxes
        self.frame_analisis = ttk.LabelFrame(frame, text="Análisis Disponibles", padding=10)
        self.frame_analisis.grid(row=2, column=1, sticky='w', pady=10)
        
        self.analisis_vars = {}
        self.cargar_analisis_disponibles()
        
        # Botón para actualizar lista de análisis
        ttk.Button(
            frame,
            text="Actualizar Lista de Análisis",
            command=self.cargar_analisis_disponibles
        ).grid(row=3, column=1, pady=5, sticky='w')
        
        ttk.Button(
            frame, 
            text="Registrar Orden",
            command=self.registrar_orden_click
        ).grid(row=4, column=1, pady=20, sticky='w')
        
        # Área de información de IDs de resultados creados
        ttk.Label(frame, text="IDs DE RESULTADOS CREADOS", font=('Arial', 12, 'bold')).grid(
            row=5, column=0, columnspan=2, pady=(20, 10)
        )
        
        self.text_ids_resultados = tk.Text(frame, height=4, width=80, state='disabled')
        self.text_ids_resultados.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Área de información
        ttk.Label(frame, text="ÓRDENES RECIENTES", font=('Arial', 12, 'bold')).grid(
            row=7, column=0, columnspan=2, pady=(20, 10)
        )
        
        self.text_ordenes = tk.Text(frame, height=12, width=80, state='disabled')
        self.text_ordenes.grid(row=8, column=0, columnspan=2, pady=5)
        
        ttk.Button(
            frame,
            text="Actualizar Lista",
            command=self.actualizar_ordenes_recientes
        ).grid(row=9, column=1, pady=5, sticky='e')
    
    def cargar_analisis_disponibles(self):
        """Cargar análisis disponibles dinámicamente desde la BD"""
        from funcionalidades_extra import FuncionalidadesExtra
        extra = FuncionalidadesExtra()
        
        # Limpiar checkboxes existentes
        for widget in self.frame_analisis.winfo_children():
            widget.destroy()
        
        self.analisis_vars.clear()
        
        # Cargar análisis desde BD
        analisis_list = extra.listar_tipos_analisis()
        
        for analisis in analisis_list:
            id_analisis, codigo, nombre, vmin, vmax, unidad = analisis
            var = tk.BooleanVar()
            self.analisis_vars[id_analisis] = var
            texto = f"{codigo} - {nombre} ({vmin}-{vmax} {unidad})"
            ttk.Checkbutton(self.frame_analisis, text=texto, variable=var).pack(anchor='w', pady=2)

    def registrar_orden_click(self):
        """Registrar nueva orden con transacción"""
        try:
            paciente_id = int(self.entry_paciente_id.get())
            analisis_seleccionados = [
                id_a for id_a, var in self.analisis_vars.items() if var.get()
            ]
            
            if not analisis_seleccionados:
                messagebox.showwarning("Advertencia", "Seleccione al menos un análisis")
                return
            
            # REQUISITO 1: Transacción para registrar orden
            orden_id, mensaje, ids_resultados = registrar_orden_con_analisis(
                paciente_id, analisis_seleccionados, self.usuario_actual
            )
            
            if orden_id:
                # Mostrar IDs de resultados creados
                texto_ids = f"Orden #{orden_id} - IDs de Resultados creados:\n"
                texto_ids += ", ".join(str(id_res) for id_res in ids_resultados)
                
                self.text_ids_resultados.config(state='normal')
                self.text_ids_resultados.delete(1.0, tk.END)
                self.text_ids_resultados.insert(1.0, texto_ids)
                self.text_ids_resultados.config(state='disabled')
                
                messagebox.showinfo("Éxito", 
                    f"✓ Orden #{orden_id} registrada exitosamente\n\n"
                    f"Análisis solicitados: {len(analisis_seleccionados)}\n"
                    f"Paciente ID: {paciente_id}\n"
                    f"IDs de Resultados: {', '.join(str(id_res) for id_res in ids_resultados)}\n"
                    f"{mensaje}"
                )
                self.entry_paciente_id.delete(0, tk.END)
                for var in self.analisis_vars.values():
                    var.set(False)
                self.actualizar_ordenes_recientes()
            else:
                messagebox.showerror("Error", mensaje)
                
        except ValueError:
            messagebox.showerror("Error", "ID de paciente debe ser un número válido")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    
    def actualizar_ordenes_recientes(self):
        """Mostrar las últimas órdenes registradas"""
        from database import Database
        db = Database()
        conn = db.get_connection()
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT o.id, o.paciente_id, o.fecha_orden, o.estado, o.usuario_crea,
                           COUNT(r.id) as total_analisis
                    FROM ordenes o
                    LEFT JOIN resultados r ON o.id = r.orden_id
                    GROUP BY o.id, o.paciente_id, o.fecha_orden, o.estado, o.usuario_crea
                    ORDER BY o.fecha_orden DESC
                    LIMIT 10
                """)
                
                ordenes = cursor.fetchall()
                
                texto = "ÚLTIMAS 10 ÓRDENES\n"
                texto += "="*80 + "\n\n"
                
                for orden in ordenes:
                    id_orden, pac_id, fecha, estado, usuario, total = orden
                    texto += f"Orden #{id_orden} | Paciente: {pac_id} | Estado: {estado}\n"
                    texto += f"  Análisis: {total} | Usuario: {usuario} | Fecha: {fecha}\n"
                    texto += "-"*80 + "\n"
                
                self.text_ordenes.config(state='normal')
                self.text_ordenes.delete(1.0, tk.END)
                self.text_ordenes.insert(1.0, texto)
                self.text_ordenes.config(state='disabled')
        finally:
            db.release_connection(conn)
    
    def crear_tab_resultados(self, parent):
        """TAB 3: Cargar resultados de análisis"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="CARGAR RESULTADO DE ANÁLISIS", font=('Arial', 14, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=10
        )
        
        ttk.Label(frame, text="ID del Resultado:").grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.entry_resultado_id = ttk.Entry(frame, width=30)
        self.entry_resultado_id.grid(row=1, column=1, pady=5, padx=5, sticky='w')
        
        ttk.Button(
            frame,
            text="Buscar Info",
            command=self.buscar_info_resultado
        ).grid(row=1, column=2, pady=5, padx=5)
        
        # Información del análisis
        self.label_info_analisis = ttk.Label(frame, text="", font=('Arial', 10), foreground='blue')
        self.label_info_analisis.grid(row=2, column=0, columnspan=3, pady=10)
        
        ttk.Label(frame, text="Valor del Análisis:").grid(row=3, column=0, sticky='w', pady=5, padx=5)
        self.entry_valor = ttk.Entry(frame, width=30, font=('Arial', 12))
        self.entry_valor.grid(row=3, column=1, pady=5, padx=5, sticky='w')
        
        ttk.Button(
            frame,
            text="CARGAR RESULTADO",
            command=self.cargar_resultado_click
        ).grid(row=4, column=1, pady=20, sticky='w')
        
        # Etiqueta para alertas
        self.label_alerta = ttk.Label(frame, text="", font=('Arial', 12, 'bold'))
        self.label_alerta.grid(row=5, column=0, columnspan=3, pady=10)
        
        # Sección de resultados pendientes
        ttk.Separator(frame, orient='horizontal').grid(row=6, column=0, columnspan=3, sticky='ew', pady=20)
        
        ttk.Label(frame, text="RESULTADOS PENDIENTES", font=('Arial', 12, 'bold')).grid(
            row=7, column=0, columnspan=3, pady=10
        )
        
        # Treeview para mostrar pendientes
        columns = ('ID', 'Orden', 'Análisis', 'Paciente', 'Fecha Orden')
        self.tree_pendientes = ttk.Treeview(frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.tree_pendientes.heading(col, text=col)
            self.tree_pendientes.column(col, width=150)
        
        self.tree_pendientes.grid(row=8, column=0, columnspan=3, pady=10, sticky='ew')
        
        ttk.Button(
            frame,
            text="Actualizar Pendientes",
            command=self.actualizar_pendientes
        ).grid(row=9, column=2, pady=5, sticky='e')
        
        # Cargar pendientes al iniciar
        self.actualizar_pendientes()
    
    def buscar_info_resultado(self):
        """Buscar información del análisis antes de cargar el resultado"""
        try:
            resultado_id = int(self.entry_resultado_id.get())
            
            from database import Database
            db = Database()
            conn = db.get_connection()
            
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT ta.nombre, ta.valor_min, ta.valor_max, ta.unidad
                        FROM resultados r
                        JOIN tipos_analisis ta ON r.tipo_analisis_id = ta.id
                        WHERE r.id = %s
                    """, (resultado_id,))
                    
                    info = cursor.fetchone()
                    
                    if info:
                        nombre, vmin, vmax, unidad = info
                        texto = f"{nombre} | Rango Normal: {vmin}-{vmax} {unidad}"
                        self.label_info_analisis.config(text=texto)
                    else:
                        messagebox.showwarning("No encontrado", f"No existe resultado con ID {resultado_id}")
            finally:
                db.release_connection(conn)
                
        except ValueError:
            messagebox.showerror("Error", "ID debe ser un número")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def cargar_resultado_click(self):
        """Cargar resultado con validación de rango"""
        try:
            resultado_id = int(self.entry_resultado_id.get())
            valor = float(self.entry_valor.get())
            
            # REQUISITO 1 y 5: Transacción con validación transaccional
            success, fuera_rango, mensaje = cargar_resultado_con_validacion(
                resultado_id, valor, self.usuario_actual
            )
            
            if success:
                if fuera_rango:
                    self.label_alerta.config(
                        text="ALERTA: VALOR FUERA DE RANGO NORMAL",
                        foreground="red"
                    )
                    messagebox.showwarning(
                        "Alerta de Rango",
                        f"{mensaje}\n\nEl valor {valor} está FUERA del rango normal\n"
                        "Se requiere revisión médica"
                    )
                else:
                    self.label_alerta.config(
                        text="✓ Valor dentro del rango normal",
                        foreground="green"
                    )
                    messagebox.showinfo("Éxito", f"{mensaje}\n✓ Valor dentro del rango esperado")
                
                # Limpiar campos
                self.entry_resultado_id.delete(0, tk.END)
                self.entry_valor.delete(0, tk.END)
                self.label_info_analisis.config(text="")
                
                # Actualizar lista de pendientes
                self.actualizar_pendientes()
            else:
                messagebox.showerror("Error", mensaje)
                
        except ValueError:
            messagebox.showerror("Error", "Datos inválidos. Verifique ID y valor numérico")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    
    def actualizar_pendientes(self):
        """Actualizar lista de resultados pendientes"""
        # Limpiar tabla
        for item in self.tree_pendientes.get_children():
            self.tree_pendientes.delete(item)
        
        from database import Database
        db = Database()
        conn = db.get_connection()
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT r.id, r.orden_id, ta.nombre, o.paciente_id, o.fecha_orden
                    FROM resultados r
                    JOIN tipos_analisis ta ON r.tipo_analisis_id = ta.id
                    JOIN ordenes o ON r.orden_id = o.id
                    WHERE r.valor IS NULL
                    ORDER BY o.fecha_orden DESC
                    LIMIT 50
                """)
                
                pendientes = cursor.fetchall()
                
                for row in pendientes:
                    self.tree_pendientes.insert('', 'end', values=row)
        finally:
            db.release_connection(conn)
    
    def crear_tab_estadisticas(self, parent):
        """TAB 4: Estadísticas y reportes"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="ESTADÍSTICAS DE ANÁLISIS", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Frame para selección de fechas
        frame_fechas = ttk.LabelFrame(frame, text="Período de Análisis", padding=10)
        frame_fechas.pack(pady=10)
        
        ttk.Label(frame_fechas, text="Desde:").grid(row=0, column=0, padx=5)
        self.entry_fecha_desde = ttk.Entry(frame_fechas, width=15)
        self.entry_fecha_desde.insert(0, (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        self.entry_fecha_desde.grid(row=0, column=1, padx=5)
        
        ttk.Label(frame_fechas, text="Hasta:").grid(row=0, column=2, padx=5)
        self.entry_fecha_hasta = ttk.Entry(frame_fechas, width=15)
        self.entry_fecha_hasta.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.entry_fecha_hasta.grid(row=0, column=3, padx=5)
        
        ttk.Button(
            frame_fechas,
            text="Generar Estadísticas",
            command=self.mostrar_estadisticas
        ).grid(row=0, column=4, padx=10)
        
        # Treeview para estadísticas
        columns = ('Análisis', 'Total', 'Promedio', 'Mínimo', 'Máximo', 'Fuera Rango', '% Fuera')
        self.tree_stats = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree_stats.heading(col, text=col)
            self.tree_stats.column(col, width=130)
        
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.tree_stats.yview)
        self.tree_stats.configure(yscrollcommand=scrollbar.set)
        
        self.tree_stats.pack(side='left', fill='both', expand=True, pady=10)
        scrollbar.pack(side='right', fill='y')
        
        # Cargar estadísticas iniciales
        self.mostrar_estadisticas()
    
    def mostrar_estadisticas(self):
        """REQUISITO 6: Mostrar estadísticas optimizadas por período"""
        # Limpiar tabla
        for item in self.tree_stats.get_children():
            self.tree_stats.delete(item)
        
        try:
            fecha_desde = self.entry_fecha_desde.get()
            fecha_hasta = self.entry_fecha_hasta.get()
            
            # REQUISITO 6: Consulta optimizada de estadísticas
            estadisticas = obtener_estadisticas_periodo(fecha_desde, fecha_hasta)
            
            if not estadisticas:
                messagebox.showinfo("Sin datos", "No hay resultados en el período seleccionado")
                return
            
            for row in estadisticas:
                self.tree_stats.insert('', 'end', values=row)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar estadísticas: {str(e)}")
    
    def crear_tab_auditoria(self, parent):
        """TAB 5: Consultar auditoría de accesos"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="AUDITORÍA DE ACCESOS", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Frame de búsqueda
        frame_buscar = ttk.Frame(frame)
        frame_buscar.pack(pady=10)
        
        ttk.Label(frame_buscar, text="ID de Resultado:").grid(row=0, column=0, padx=5)
        self.entry_audit_id = ttk.Entry(frame_buscar, width=20)
        self.entry_audit_id.grid(row=0, column=1, padx=5)
        
        ttk.Button(
            frame_buscar,
            text="Consultar Auditoría",
            command=self.consultar_auditoria
        ).grid(row=0, column=2, padx=10)
        
        # Treeview para auditoría
        columns = ('Fecha', 'Acción', 'Usuario', 'Detalles', 'IP')
        self.tree_audit = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        
        anchos = [180, 80, 120, 300, 120]
        for col, ancho in zip(columns, anchos):
            self.tree_audit.heading(col, text=col)
            self.tree_audit.column(col, width=ancho)
        
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.tree_audit.yview)
        self.tree_audit.configure(yscrollcommand=scrollbar.set)
        
        self.tree_audit.pack(side='left', fill='both', expand=True, pady=10)
        scrollbar.pack(side='right', fill='y')
    
    def consultar_auditoria(self):
        """REQUISITO 4: Consultar trazabilidad completa de accesos"""
        try:
            resultado_id = int(self.entry_audit_id.get())
            
            # Limpiar tabla
            for item in self.tree_audit.get_children():
                self.tree_audit.delete(item)
            
            from auditoria import consultar_auditoria_resultado
            registros = consultar_auditoria_resultado(resultado_id)
            
            if not registros:
                messagebox.showinfo("Sin registros", f"No hay auditoría para el resultado ID {resultado_id}")
                return
            
            for row in registros:
                self.tree_audit.insert('', 'end', values=row)
                
            messagebox.showinfo("Éxito", f"Se encontraron {len(registros)} registros de auditoría")
                
        except ValueError:
            messagebox.showerror("Error", "ID debe ser un número")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")

    def crear_tab_administracion(self, parent):
        """TAB EXTRA: Administración del sistema"""
        from funcionalidades_extra import FuncionalidadesExtra
        self.extra = FuncionalidadesExtra()
        
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Notebook secundario para sub-secciones
        sub_notebook = ttk.Notebook(frame)
        
        # Sub-tab 1: Gestión de Análisis
        tab_analisis = ttk.Frame(sub_notebook)
        self.crear_subtab_analisis(tab_analisis)
        sub_notebook.add(tab_analisis, text="Tipos de Análisis")
        
        # Sub-tab 2: Búsquedas Avanzadas
        tab_busquedas = ttk.Frame(sub_notebook)
        self.crear_subtab_busquedas(tab_busquedas)
        sub_notebook.add(tab_busquedas, text="Búsquedas")
        
        # Sub-tab 3: Reportes
        tab_reportes = ttk.Frame(sub_notebook)
        self.crear_subtab_reportes(tab_reportes)
        sub_notebook.add(tab_reportes, text="Reportes")
        
        # Sub-tab 4: Alertas
        tab_alertas = ttk.Frame(sub_notebook)
        self.crear_subtab_alertas(tab_alertas)
        sub_notebook.add(tab_alertas, text="Alertas")
        
        sub_notebook.pack(expand=True, fill='both')

        # Sub-tab 5: Modificación de Datos
        tab_modificar = ttk.Frame(sub_notebook)
        self.crear_subtab_modificacion(tab_modificar)
        sub_notebook.add(tab_modificar, text="Modificar Datos")
    def crear_subtab_analisis(self, parent):
        """Gestión de tipos de análisis"""
        frame = ttk.LabelFrame(parent, text="Agregar Nuevo Tipo de Análisis", padding=10)
        frame.pack(padx=10, pady=10, fill='x')
        
        ttk.Label(frame, text="Código:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_nuevo_codigo = ttk.Entry(frame, width=20)
        self.entry_nuevo_codigo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Nombre:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.entry_nuevo_nombre = ttk.Entry(frame, width=40)
        self.entry_nuevo_nombre.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Valor Mínimo:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.entry_nuevo_min = ttk.Entry(frame, width=20)
        self.entry_nuevo_min.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(frame, text="Valor Máximo:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.entry_nuevo_max = ttk.Entry(frame, width=20)
        self.entry_nuevo_max.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(frame, text="Unidad:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.entry_nuevo_unidad = ttk.Entry(frame, width=20)
        self.entry_nuevo_unidad.grid(row=4, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Button(frame, text="Agregar Análisis", 
                command=self.agregar_tipo_analisis).grid(row=5, column=1, pady=10, sticky='w')
        
        # Lista de análisis existentes
        frame_lista = ttk.LabelFrame(parent, text="Tipos de Análisis Registrados", padding=10)
        frame_lista.pack(padx=10, pady=10, fill='both', expand=True)
        
        columns = ('ID', 'Código', 'Nombre', 'Min', 'Max', 'Unidad')
        self.tree_analisis = ttk.Treeview(frame_lista, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree_analisis.heading(col, text=col)
            self.tree_analisis.column(col, width=100)
        
        self.tree_analisis.pack(fill='both', expand=True)
        
        ttk.Button(frame_lista, text="Actualizar Lista",
                command=self.actualizar_lista_analisis).pack(pady=5)
        
        self.actualizar_lista_analisis()
    def agregar_tipo_analisis(self):
        """Agregar nuevo tipo de análisis"""
        from funcionalidades_extra import FuncionalidadesExtra
        extra = FuncionalidadesExtra()
        
        try:
            codigo = self.entry_nuevo_codigo.get().strip()
            nombre = self.entry_nuevo_nombre.get().strip()
            vmin = float(self.entry_nuevo_min.get())
            vmax = float(self.entry_nuevo_max.get())
            unidad = self.entry_nuevo_unidad.get().strip()
            
            if not codigo or not nombre:
                messagebox.showwarning("Advertencia", "Código y nombre son obligatorios")
                return
            
            nuevo_id, mensaje = extra.agregar_tipo_analisis(codigo, nombre, vmin, vmax, unidad)
            
            if nuevo_id:
                messagebox.showinfo("Éxito", f"Análisis agregado con ID: {nuevo_id}")
                self.actualizar_lista_analisis()
                # Limpiar campos
                self.entry_nuevo_codigo.delete(0, tk.END)
                self.entry_nuevo_nombre.delete(0, tk.END)
                self.entry_nuevo_min.delete(0, tk.END)
                self.entry_nuevo_max.delete(0, tk.END)
                self.entry_nuevo_unidad.delete(0, tk.END)
            else:
                messagebox.showerror("Error", mensaje)
        except ValueError:
            messagebox.showerror("Error", "Valores mínimo y máximo deben ser numéricos")
    def actualizar_lista_analisis(self):
        """Actualizar lista de tipos de análisis"""
        from funcionalidades_extra import FuncionalidadesExtra
        extra = FuncionalidadesExtra()
        
        # Limpiar
        for item in self.tree_analisis.get_children():
            self.tree_analisis.delete(item)
        
        # Cargar
        analisis = extra.listar_tipos_analisis()
        for row in analisis:
            self.tree_analisis.insert('', 'end', values=row)
    def crear_subtab_busquedas(self, parent):
        """Búsquedas avanzadas"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="BÚSQUEDAS AVANZADAS", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Búsqueda por DNI
        frame_dni = ttk.LabelFrame(frame, text="Buscar por DNI", padding=10)
        frame_dni.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_dni, text="DNI:").pack(side='left', padx=5)
        self.entry_buscar_dni = ttk.Entry(frame_dni, width=30)
        self.entry_buscar_dni.pack(side='left', padx=5)
        ttk.Button(frame_dni, text="Buscar", command=self.buscar_por_dni).pack(side='left', padx=5)
        
        # Búsqueda por nombre
        frame_nombre = ttk.LabelFrame(frame, text="Buscar por Nombre", padding=10)
        frame_nombre.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_nombre, text="Nombre:").pack(side='left', padx=5)
        self.entry_buscar_nombre = ttk.Entry(frame_nombre, width=30)
        self.entry_buscar_nombre.pack(side='left', padx=5)
        ttk.Button(frame_nombre, text="Buscar", command=self.buscar_por_nombre).pack(side='left', padx=5)
        
        # Resultados
        self.text_busqueda = tk.Text(frame, height=20, width=80, state='disabled')
        self.text_busqueda.pack(fill='both', expand=True, padx=10, pady=10)
        # Botón para ver historial completo
        frame_historial = ttk.Frame(frame)
        frame_historial.pack(fill='x', padx=10, pady=10)

        ttk.Label(frame_historial, text="Ver Historial Completo:").pack(side='left', padx=5)
        self.entry_historial_id = ttk.Entry(frame_historial, width=20)
        self.entry_historial_id.pack(side='left', padx=5)
        ttk.Button(frame_historial, text="Ver Historial", 
        command=self.ver_historial_completo).pack(side='left', padx=5)
    def buscar_por_dni(self):
        """Buscar paciente por DNI"""
        from funcionalidades_extra import FuncionalidadesExtra
        extra = FuncionalidadesExtra()
        
        dni = self.entry_buscar_dni.get().strip()
        if not dni:
            messagebox.showwarning("Advertencia", "Ingrese un DNI")
            return
        
        resultado = extra.buscar_paciente_por_dni(dni)
        
        self.text_busqueda.config(state='normal')
        self.text_busqueda.delete(1.0, tk.END)
        
        if resultado:
            texto = f"""
        PACIENTE ENCONTRADO
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ID: {resultado['id']}
        Nombre: {resultado['nombre']}
        DNI: {resultado['dni']}
        Fecha Nacimiento: {resultado['fecha_nacimiento']}
        Teléfono: {resultado['telefono']}
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """
            self.text_busqueda.insert(1.0, texto)
        else:
            self.text_busqueda.insert(1.0, "No se encontró paciente con ese DNI")
        
        self.text_busqueda.config(state='disabled')
    def buscar_por_nombre(self):
        """Buscar pacientes por nombre"""
        from funcionalidades_extra import FuncionalidadesExtra
        extra = FuncionalidadesExtra()
        
        nombre = self.entry_buscar_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Advertencia", "Ingrese un nombre")
            return
        
        resultados = extra.buscar_paciente_por_nombre(nombre)
        
        self.text_busqueda.config(state='normal')
        self.text_busqueda.delete(1.0, tk.END)
        
        if resultados:
            texto = f"RESULTADOS ENCONTRADOS: {len(resultados)}\n"
            texto += "="*60 + "\n\n"
            
            for pac in resultados:
                texto += f"ID: {pac['id']} | {pac['nombre']} | DNI: {pac['dni']}\n"
            
            self.text_busqueda.insert(1.0, texto)
        else:
            self.text_busqueda.insert(1.0, "No se encontraron pacientes con ese nombre")
        
        self.text_busqueda.config(state='disabled')

    def ver_historial_completo(self):
        """Ver historial completo de análisis de un paciente"""
        from funcionalidades_extra import FuncionalidadesExtra
        extra = FuncionalidadesExtra()
        
        try:
            paciente_id = int(self.entry_historial_id.get())
            historial = extra.obtener_historial_paciente(paciente_id)
            
            self.text_busqueda.config(state='normal')
            self.text_busqueda.delete(1.0, tk.END)
            
            if historial:
                texto = f"HISTORIAL COMPLETO - PACIENTE ID: {paciente_id}\n"
                texto += "="*70 + "\n\n"
                
                orden_actual = None
                for row in historial:
                    orden_id, fecha_orden, estado, analisis, valor, fecha_res, fuera, vmin, vmax, unidad = row
                    
                    if orden_id != orden_actual:
                        texto += f"\n{'─'*70}\n"
                        texto += f"ORDEN #{orden_id} - {fecha_orden} - Estado: {estado}\n"
                        texto += f"{'─'*70}\n"
                        orden_actual = orden_id
                    
                    alerta = " FUERA DE RANGO" if fuera else ""
                    texto += f"  • {analisis}: {valor} {unidad} (Rango: {vmin}-{vmax}){alerta}\n"
                    if fecha_res:
                        texto += f"    Fecha resultado: {fecha_res}\n"
                
                self.text_busqueda.insert(1.0, texto)
            else:
                self.text_busqueda.insert(1.0, "No se encontró historial para este paciente")
            
            self.text_busqueda.config(state='disabled')
        except ValueError:
            messagebox.showerror("Error", "ID debe ser numérico")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def crear_subtab_reportes(self, parent):
        """Generación de reportes"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="GENERACIÓN DE REPORTES", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Reporte de paciente
        frame_pac = ttk.LabelFrame(frame, text="Reporte Completo de Paciente", padding=10)
        frame_pac.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_pac, text="ID Paciente:").pack(side='left', padx=5)
        self.entry_reporte_paciente = ttk.Entry(frame_pac, width=20)
        self.entry_reporte_paciente.pack(side='left', padx=5)
        ttk.Button(frame_pac, text="Generar Reporte TXT",
                command=self.generar_reporte_paciente).pack(side='left', padx=5)
        
        # Export CSV de orden
        frame_csv = ttk.LabelFrame(frame, text="Exportar Resultados a CSV", padding=10)
        frame_csv.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_csv, text="ID Orden:").pack(side='left', padx=5)
        self.entry_export_orden = ttk.Entry(frame_csv, width=20)
        self.entry_export_orden.pack(side='left', padx=5)
        ttk.Button(frame_csv, text="Exportar CSV",
                command=self.exportar_csv).pack(side='left', padx=5)
        # Estadísticas de paciente específico
        frame_stats_pac = ttk.LabelFrame(frame, text="Estadísticas de Paciente", padding=10)
        frame_stats_pac.pack(fill='x', padx=10, pady=10)

        ttk.Label(frame_stats_pac, text="ID Paciente:").pack(side='left', padx=5)
        self.entry_stats_paciente = ttk.Entry(frame_stats_pac, width=20)
        self.entry_stats_paciente.pack(side='left', padx=5)
        ttk.Button(frame_stats_pac, text="Ver Estadísticas",
                command=self.ver_estadisticas_paciente).pack(side='left', padx=5)

        # Área de resultados de estadísticas
        self.text_stats_paciente = tk.Text(frame, height=15, width=80, state='disabled')
        self.text_stats_paciente.pack(fill='both', expand=True, padx=10, pady=10)
    def generar_reporte_paciente(self):
        """Generar reporte de paciente"""
        from funcionalidades_extra import FuncionalidadesExtra
        extra = FuncionalidadesExtra()
        
        try:
            paciente_id = int(self.entry_reporte_paciente.get())
            success, mensaje = extra.generar_reporte_paciente(paciente_id)
            
            if success:
                messagebox.showinfo("Éxito", mensaje)
            else:
                messagebox.showerror("Error", mensaje)
        except ValueError:
            messagebox.showerror("Error", "ID debe ser numérico")
    def exportar_csv(self):
        """Exportar resultados a CSV"""
        from funcionalidades_extra import FuncionalidadesExtra
        extra = FuncionalidadesExtra()
        try:
            orden_id = int(self.entry_export_orden.get())
            success, mensaje = extra.exportar_resultados_csv(orden_id)
            
            if success:
                messagebox.showinfo("Éxito", mensaje)
            else:
                messagebox.showerror("Error", mensaje)
        except ValueError:
            messagebox.showerror("Error", "ID debe ser numérico")

    def ver_estadisticas_paciente(self):
        """Ver estadísticas de un paciente específico"""
        from estadisticas import obtener_estadisticas_paciente
        
        try:
            paciente_id = int(self.entry_stats_paciente.get())
            stats = obtener_estadisticas_paciente(paciente_id)
            
            self.text_stats_paciente.config(state='normal')
            self.text_stats_paciente.delete(1.0, tk.END)
            
            if stats:
                texto = f"ESTADÍSTICAS - PACIENTE ID: {paciente_id}\n"
                texto += "="*70 + "\n\n"
                texto += f"{'Análisis':<25} {'Valor':<12} {'Fecha':<20} {'Estado':<15}\n"
                texto += "-"*70 + "\n"
                
                for row in stats:
                    nombre, valor, fecha, fuera, vmin, vmax, unidad = row
                    estado = "FUERA" if fuera else "✓ Normal"
                    fecha_str = fecha.strftime('%Y-%m-%d %H:%M') if fecha else "N/A"
                    texto += f"{nombre:<25} {valor:<6}{unidad:<6} {fecha_str:<20} {estado:<15}\n"
                    texto += f"  Rango normal: {vmin}-{vmax} {unidad}\n\n"
                
                self.text_stats_paciente.insert(1.0, texto)
            else:
                self.text_stats_paciente.insert(1.0, "No hay estadísticas para este paciente")
            
            self.text_stats_paciente.config(state='disabled')
        except ValueError:
            messagebox.showerror("Error", "ID debe ser numérico")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    def crear_subtab_alertas(self, parent):
        """Sistema de alertas"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text="ALERTAS URGENTES", font=('Arial', 14, 'bold')).pack(pady=10)
        ttk.Label(frame, text="Resultados fuera de rango de los últimos 7 días:").pack()
        # Treeview de alertas
        columns = ('ID', 'Orden', 'Paciente', 'Análisis', 'Valor', 'Rango', 'Tipo')
        self.tree_alertas = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        anchos = [60, 80, 80, 200, 80, 120, 80]
        for col, ancho in zip(columns, anchos):
            self.tree_alertas.heading(col, text=col)
            self.tree_alertas.column(col, width=ancho)
        self.tree_alertas.pack(fill='both', expand=True, pady=10)
        ttk.Button(frame, text="Actualizar Alertas",
                command=self.actualizar_alertas).pack(pady=5)
        self.actualizar_alertas()
        # Frame para marcar alerta como revisada
        frame_revisar = ttk.LabelFrame(frame, text="Marcar Alerta como Revisada", padding=10)
        frame_revisar.pack(fill='x', padx=10, pady=10)

        ttk.Label(frame_revisar, text="ID Resultado:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_alerta_id = ttk.Entry(frame_revisar, width=15)
        self.entry_alerta_id.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_revisar, text="Observaciones:").grid(row=1, column=0, padx=5, pady=5, sticky='nw')
        self.text_observaciones = tk.Text(frame_revisar, height=3, width=50)
        self.text_observaciones.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(frame_revisar, text="Marcar como Revisada",
                command=self.marcar_alerta_revisada).grid(row=2, column=1, pady=10, sticky='w')
    def actualizar_alertas(self):
        """Actualizar lista de alertas"""
        from funcionalidades_extra import FuncionalidadesExtra
        extra = FuncionalidadesExtra()
        # Limpiar
        for item in self.tree_alertas.get_children():
            self.tree_alertas.delete(item)
        # Cargar alertas
        alertas = extra.obtener_alertas_urgentes()
        for alerta in alertas:
            res_id, ord_id, pac_id, analisis, valor, vmin, vmax, unidad, fecha, tipo = alerta
            rango_texto = f"{vmin}-{vmax} {unidad}"
            valores = (res_id, ord_id, pac_id, analisis, f"{valor} {unidad}", rango_texto, tipo)
            self.tree_alertas.insert('', 'end', values=valores)

    def crear_subtab_modificacion(self, parent):
        """Modificación de pacientes y cancelación de órdenes"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Modificar paciente
        frame_mod_pac = ttk.LabelFrame(frame, text="Modificar Datos de Paciente", padding=10)
        frame_mod_pac.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_mod_pac, text="ID Paciente:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_mod_pac_id = ttk.Entry(frame_mod_pac, width=20)
        self.entry_mod_pac_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_mod_pac, text="Nuevo Nombre:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.entry_mod_nombre = ttk.Entry(frame_mod_pac, width=40)
        self.entry_mod_nombre.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_mod_pac, text="Nuevo Teléfono:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.entry_mod_telefono = ttk.Entry(frame_mod_pac, width=40)
        self.entry_mod_telefono.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(frame_mod_pac, text="Modificar Paciente",
                command=self.modificar_paciente).grid(row=3, column=1, pady=10, sticky='w')
        
        # Cancelar orden
        frame_cancel = ttk.LabelFrame(frame, text="Cancelar Orden", padding=10)
        frame_cancel.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_cancel, text="ID Orden:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_cancel_orden = ttk.Entry(frame_cancel, width=20)
        self.entry_cancel_orden.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_cancel, text="Motivo:").grid(row=1, column=0, sticky='nw', padx=5, pady=5)
        self.text_motivo_cancel = tk.Text(frame_cancel, height=3, width=50)
        self.text_motivo_cancel.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(frame_cancel, text="Cancelar Orden",
                command=self.cancelar_orden).grid(row=2, column=1, pady=10, sticky='w')
        
        # Modificar rangos de análisis
        frame_mod_rangos = ttk.LabelFrame(frame, text="Modificar Rangos de Análisis", padding=10)
        frame_mod_rangos.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_mod_rangos, text="ID Tipo Análisis:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_mod_tipo_id = ttk.Entry(frame_mod_rangos, width=20)
        self.entry_mod_tipo_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_mod_rangos, text="Nuevo Mínimo:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.entry_mod_min = ttk.Entry(frame_mod_rangos, width=20)
        self.entry_mod_min.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_mod_rangos, text="Nuevo Máximo:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.entry_mod_max = ttk.Entry(frame_mod_rangos, width=20)
        self.entry_mod_max.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(frame_mod_rangos, text="Modificar Rangos",
                command=self.modificar_rangos).grid(row=3, column=1, pady=10, sticky='w')

    def modificar_paciente(self):
        """Modificar datos de un paciente"""
        from funcionalidades_extra import FuncionalidadesExtra
        extra = FuncionalidadesExtra()
        
        try:
            paciente_id = int(self.entry_mod_pac_id.get())
            nombre = self.entry_mod_nombre.get().strip()
            telefono = self.entry_mod_telefono.get().strip()
            
            if not nombre and not telefono:
                messagebox.showwarning("Advertencia", "Ingrese al menos un dato a modificar")
                return
            
            success, mensaje = extra.modificar_paciente(
                paciente_id, 
                nombre if nombre else None, 
                telefono if telefono else None
            )
            
            if success:
                messagebox.showinfo("Éxito", mensaje)
                self.entry_mod_pac_id.delete(0, tk.END)
                self.entry_mod_nombre.delete(0, tk.END)
                self.entry_mod_telefono.delete(0, tk.END)
            else:
                messagebox.showerror("Error", mensaje)
        except ValueError:
            messagebox.showerror("Error", "ID debe ser numérico")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")

    def cancelar_orden(self):
        """Cancelar una orden"""
        from funcionalidades_extra import FuncionalidadesExtra
        extra = FuncionalidadesExtra()
        
        try:
            orden_id = int(self.entry_cancel_orden.get())
            motivo = self.text_motivo_cancel.get(1.0, tk.END).strip()
            
            if not motivo:
                messagebox.showwarning("Advertencia", "Ingrese el motivo de cancelación")
                return
            
            success, mensaje = extra.cancelar_orden(orden_id, self.usuario_actual, motivo)
            
            if success:
                messagebox.showinfo("Éxito", mensaje)
                self.entry_cancel_orden.delete(0, tk.END)
                self.text_motivo_cancel.delete(1.0, tk.END)
            else:
                messagebox.showerror("Error", mensaje)
        except ValueError:
            messagebox.showerror("Error", "ID debe ser numérico")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")

    def modificar_rangos(self):
        """Modificar rangos de un tipo de análisis"""
        from funcionalidades_extra import FuncionalidadesExtra
        extra = FuncionalidadesExtra()
        
        try:
            tipo_id = int(self.entry_mod_tipo_id.get())
            nuevo_min = float(self.entry_mod_min.get())
            nuevo_max = float(self.entry_mod_max.get())
            
            success, mensaje = extra.modificar_rangos_analisis(tipo_id, nuevo_min, nuevo_max)
            
            if success:
                messagebox.showinfo("Éxito", mensaje)
                self.entry_mod_tipo_id.delete(0, tk.END)
                self.entry_mod_min.delete(0, tk.END)
                self.entry_mod_max.delete(0, tk.END)
                self.actualizar_lista_analisis()
            else:
                messagebox.showerror("Error", mensaje)
        except ValueError:
            messagebox.showerror("Error", "Los valores deben ser numéricos")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
        
    def marcar_alerta_revisada(self):
        """Marcar una alerta como revisada"""
        from funcionalidades_extra import FuncionalidadesExtra
        extra = FuncionalidadesExtra()
        
        try:
            resultado_id = int(self.entry_alerta_id.get())
            observaciones = self.text_observaciones.get(1.0, tk.END).strip()
            
            if not observaciones:
                messagebox.showwarning("Advertencia", "Ingrese observaciones")
                return
            
            success, mensaje = extra.marcar_alerta_revisada(
                resultado_id, self.usuario_actual, observaciones
            )
            
            if success:
                messagebox.showinfo("Éxito", mensaje)
                self.entry_alerta_id.delete(0, tk.END)
                self.text_observaciones.delete(1.0, tk.END)
                self.actualizar_alertas()
            else:
                messagebox.showerror("Error", mensaje)
        except ValueError:
            messagebox.showerror("Error", "ID debe ser numérico")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")

    def run(self):
        """Iniciar la aplicación"""
        self.root.mainloop()