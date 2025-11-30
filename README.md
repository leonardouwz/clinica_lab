# ClinicalLabManager

## Sistema de Gestión de Laboratorios de Análisis Clínicos

Sistema completo para la gestión de laboratorios clínicos que maneja órdenes de análisis, resultados, trazabilidad completa y seguridad de datos sensibles mediante encriptación.

---

## Descripción del Proyecto

ClinicalLabManager es un sistema diseñado para laboratorios clínicos que permite:
- Registrar pacientes con datos encriptados
- Gestionar órdenes de análisis clínicos
- Cargar y validar resultados contra rangos normales
- Auditar todos los accesos a datos sensibles
- Generar estadísticas y reportes
- Buscar y consultar información de forma segura

---

## Tecnologías Utilizadas

### Lenguaje y Framework
- **Python 3.x** - Lenguaje principal del sistema
- **Tkinter** - Interfaz gráfica de usuario

### Base de Datos
- **PostgreSQL** - Sistema de gestión de base de datos relacional
- **psycopg2** - Adaptador de PostgreSQL para Python

### Herramientas y Librerías
- **Cryptography (Fernet)** - Encriptación de datos sensibles
- **python-dotenv** - Gestión de variables de entorno
- **CSV** - Exportación de reportes

---

## Requisitos Funcionales Implementados

### **REQUISITO 1: Transacciones ACID**
**Implementar transacciones para registro de órdenes y carga de resultados**

**Archivos:** `transacciones.py`

**Funcionalidades:**
- `registrar_orden_con_analisis()`: Crea una orden con múltiples análisis en una sola transacción atómica
- `cargar_resultado_con_validacion()`: Actualiza resultados garantizando consistencia de datos
- `registrar_paciente()`: Inserta pacientes con datos encriptados de forma transaccional

**Características:**
- Manejo de COMMIT/ROLLBACK automático
- Garantía de atomicidad: todas las operaciones se completan o ninguna
- Control de errores con reversión automática en caso de fallo

---

### **REQUISITO 2: Índices para Optimización**
**Crear índices en pacientes, órdenes y tipos de análisis**

**Archivo:** `clinica_lab.sql`

**Índices implementados:**
```sql
-- Pacientes
CREATE INDEX idx_pacientes_created ON pacientes(created_at DESC);

-- Tipos de análisis
CREATE INDEX idx_tipos_codigo ON tipos_analisis(codigo);
CREATE INDEX idx_tipos_nombre ON tipos_analisis(nombre);

-- Órdenes
CREATE INDEX idx_ordenes_paciente ON ordenes(paciente_id);
CREATE INDEX idx_ordenes_fecha ON ordenes(fecha_orden DESC);
CREATE INDEX idx_ordenes_estado ON ordenes(estado);

-- Resultados
CREATE INDEX idx_resultados_orden ON resultados(orden_id);
CREATE INDEX idx_resultados_tipo ON resultados(tipo_analisis_id);
CREATE INDEX idx_resultados_fecha ON resultados(fecha_resultado DESC);

-- Auditoría
CREATE INDEX idx_auditoria_fecha ON auditoria_accesos(fecha DESC);
CREATE INDEX idx_auditoria_usuario ON auditoria_accesos(usuario);
CREATE INDEX idx_auditoria_tabla ON auditoria_accesos(tabla, registro_id);
```

**Beneficios:**
- Búsquedas ultra-rápidas por paciente, fecha y estado
- Consultas optimizadas de auditoría
- Mejor rendimiento en estadísticas y reportes

---

### **REQUISITO 3: Encriptación de Datos Sensibles**
**Desarrollar encriptación de columnas para datos sensibles de pacientes**

**Archivos:** `config.py`, `database.py`

**Datos encriptados:**
- Nombre completo del paciente
- DNI (Documento Nacional de Identidad)
- Número de teléfono

**Implementación:**
```python
# Encriptación con Fernet (AES-128)
cipher = Fernet(ENCRYPTION_KEY)

def encriptar(texto):
    return cipher.encrypt(texto.encode())

def desencriptar(datos_enc):
    return cipher.decrypt(bytes(datos_enc)).decode()
```

**Características:**
- Clave de encriptación persistente almacenada de forma segura
- Compatibilidad con variables de entorno
- Verificación de integridad de datos

---

### **REQUISITO 4: Trazabilidad Completa**
**Gestionar trazabilidad completa con auditoría de accesos a resultados**

**Archivos:** `auditoria.py`, triggers en `clinica_lab.sql`

**Sistema de auditoría:**
- Tabla `auditoria_accesos` con registro de:
  - Tabla afectada
  - ID del registro
  - Acción realizada (CREATE, UPDATE, DELETE)
  - Usuario responsable
  - Fecha y hora exacta
  - IP del usuario
  - Detalles adicionales

**Triggers automáticos:**
```sql
CREATE TRIGGER trg_auditar_pacientes
AFTER INSERT OR UPDATE OR DELETE ON pacientes
FOR EACH ROW EXECUTE FUNCTION registrar_auditoria();
```

**Funcionalidades:**
- `registrar_auditoria()`: Registra cada acceso a datos sensibles
- `consultar_auditoria_resultado()`: Consulta historial completo de accesos

---

### **REQUISITO 5: Validaciones Transaccionales**
**Implementar validaciones transaccionales para rangos de valores normales**

**Archivos:** `transacciones.py`, `validaciones.py`

**Validación automática:**
```python
# Detecta si el valor está fuera del rango normal
if valor < valor_min or valor > valor_max:
    fuera_rango = True
```

**Niveles de alerta:**
- **NORMAL**: Valor dentro del rango
- **LEVE**: Desviación < 10%
- **MODERADO**: Desviación 10-30%
- **CRÍTICO**: Desviación > 30%

**Características:**
- Marcado automático de resultados fuera de rango
- Alertas visuales en la interfaz
- Registro en auditoría de valores anormales

---

### **REQUISITO 6: Optimización de Estadísticas**
**Optimizar consultas de estadísticas de análisis realizados por período**

**Archivo:** `estadisticas.py`

**Funcionalidades:**
```python
def obtener_estadisticas_periodo(fecha_inicio, fecha_fin):
    # Consulta optimizada con índices en fecha_resultado
    # Agrupa por tipo de análisis
    # Calcula: total, promedio, mínimo, máximo, % fuera de rango
```

**Métricas calculadas:**
- Total de análisis realizados por tipo
- Promedios, valores mínimos y máximos
- Cantidad y porcentaje de resultados fuera de rango
- Distribución temporal de análisis

---

## Estructura de la Base de Datos

### Tablas principales:

**pacientes**
- `id` (PK)
- `nombre_enc` (BYTEA) - Encriptado
- `dni_enc` (BYTEA) - Encriptado
- `fecha_nacimiento`
- `telefono_enc` (BYTEA) - Encriptado

**tipos_analisis**
- `id` (PK)
- `codigo` (UNIQUE)
- `nombre`
- `valor_min`, `valor_max`
- `unidad`

**ordenes**
- `id` (PK)
- `paciente_id` (FK)
- `fecha_orden`
- `estado` (PENDIENTE, EN PROCESO, COMPLETADO)
- `usuario_crea`

**resultados**
- `id` (PK)
- `orden_id` (FK)
- `tipo_analisis_id` (FK)
- `valor`
- `fuera_rango` (BOOLEAN)
- `fecha_resultado`
- `usuario_carga`

**auditoria_accesos**
- `id` (PK)
- `tabla`
- `registro_id`
- `accion`
- `usuario`
- `fecha`
- `ip_address`
- `detalles`

---

## Instalación y Configuración

### Requisitos previos:
```bash
- Python 3.8+
- PostgreSQL 12+
- pip (gestor de paquetes de Python)
```

### Paso 1: Clonar o descargar el proyecto
```bash
# Estructura del proyecto
ClinicalLabManager/
├── config.py
├── database.py
├── transacciones.py
├── auditoria.py
├── estadisticas.py
├── validaciones.py
├── funcionalidades_extra.py
├── interfaz.py
├── main.py
├── clinica_lab.sql
└── requirements.txt
```

### Paso 2: Instalar dependencias
```bash
pip install psycopg2-binary cryptography python-dotenv
```

### Paso 3: Configurar PostgreSQL
```bash
# Crear base de datos
psql -U postgres
CREATE DATABASE clinica_lab;
\q

# Ejecutar script SQL
psql -U postgres -d clinica_lab -f clinica_lab.sql
```

### Paso 4: Configurar variables de entorno
Crear archivo `.env` en la raíz del proyecto:
```env
DB_HOST=localhost
DB_NAME=clinica_lab
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_PORT=5432
```

### Paso 5: Ejecutar el sistema
```bash
python main.py
```

---

## Uso del Sistema

### Interfaz Gráfica

El sistema cuenta con 6 pestañas principales:

#### **1. Pacientes**
- Registrar nuevos pacientes con datos encriptados
- Buscar pacientes por ID
- Visualizar información desencriptada

**Uso:**
1. Completar formulario (Nombre, DNI, Fecha nacimiento, Teléfono)
2. Clic en "Registrar Paciente"
3. El sistema encripta automáticamente los datos sensibles

#### **2. Nueva Orden**
- Crear órdenes de análisis
- Seleccionar múltiples tipos de análisis
- Asociar orden a un paciente

**Uso:**
1. Ingresar ID del paciente
2. Seleccionar análisis requeridos (checkboxes)
3. Clic en "Registrar Orden"
4. Ver órdenes recientes en la tabla inferior

#### **3. Cargar Resultados**
- Ingresar valores de análisis
- Validación automática de rangos
- Alertas de valores anormales

**Uso:**
1. Buscar resultado pendiente por ID
2. Sistema muestra el rango normal esperado
3. Ingresar valor del análisis
4. Sistema valida y alerta si está fuera de rango
5. Actualiza automáticamente el estado de la orden

#### **4. Estadísticas**
- Visualizar métricas por período
- Análisis más frecuentes
- Porcentaje de resultados fuera de rango

**Uso:**
1. Seleccionar rango de fechas
2. Clic en "Generar Estadísticas"
3. Ver tabla con métricas calculadas

#### **5. Auditoría**
- Consultar historial de accesos
- Trazabilidad completa de resultados
- Ver quién, cuándo y qué modificó

**Uso:**
1. Ingresar ID de resultado
2. Clic en "Consultar Auditoría"
3. Ver todos los accesos registrados

#### **6. Administración**
Sub-pestañas con funcionalidades avanzadas:

**Tipos de Análisis:**
- Agregar nuevos tipos de análisis
- Modificar rangos normales
- Listar análisis existentes

**Búsquedas:**
- Buscar pacientes por DNI
- Buscar por nombre (parcial)
- Ver historial completo de análisis

**Reportes:**
- Generar reporte TXT de paciente
- Exportar resultados a CSV
- Ver estadísticas individuales

**Alertas:**
- Resultados fuera de rango de últimos 7 días
- Marcar alertas como revisadas
- Sistema de seguimiento

**Modificar Datos:**
- Actualizar información de pacientes
- Cancelar órdenes con motivo
- Modificar rangos de análisis

---

## Scripts Adicionales

### `insert_massive_data.py`
Genera datos de prueba masivos para testing:
```bash
python insert_massive_data.py
```
- Inserta miles de pacientes
- Crea órdenes automáticas
- Genera resultados aleatorios
- Útil para probar rendimiento

### `test_performance.py`
Mide el rendimiento de consultas optimizadas:
```bash
python test_performance.py
```
- Evalúa tiempo de ejecución
- Verifica uso de índices
- Compara velocidad de operaciones

### `verify_encryption.py`
Verifica el estado del sistema de encriptación:
```bash
python verify_encryption.py
```
- Comprueba clave de encriptación
- Prueba desencriptación de datos
- Diagnóstico de problemas

---

## Seguridad

### Encriptación
- Algoritmo: **Fernet (AES-128 en modo CBC)**
- Clave almacenada en: `encryption.key` o variable de entorno
- **IMPORTANTE:** Guardar backup de la clave - sin ella los datos son irrecuperables

### Auditoría
- Registro de TODAS las operaciones sensibles
- Trazabilidad completa de accesos
- Imposible modificar datos sin dejar rastro

### Validaciones
- Rangos normales configurables por análisis
- Alertas automáticas de valores críticos
- Sistema de revisión de alertas

---

## Notas Importantes

### Backup de Clave de Encriptación
```bash
# Hacer backup de la clave
cp encryption.key encryption.key.backup

# O exportar como variable de entorno
export ENCRYPTION_KEY=$(cat encryption.key)
```

### 🔄 Restaurar Sistema
Si se pierde la clave de encriptación:
1. Los datos encriptados serán IRRECUPERABLES
2. Será necesario resetear el sistema y reingresar datos
3. Mantener siempre backup de `encryption.key`

### Producción
Para ambiente de producción:
- Usar HTTPS para conexiones seguras
- Implementar sistema de autenticación robusto
- Configurar backups automáticos de PostgreSQL
- Almacenar clave de encriptación en servicio seguro (AWS KMS, Azure Key Vault)
- Habilitar SSL en conexión a PostgreSQL

---

## Soporte y Mantenimiento

### Problemas Comunes

**Error de conexión a PostgreSQL:**
```bash
# Verificar servicio
sudo systemctl status postgresql

# Verificar configuración
psql -U postgres -d clinica_lab -c "SELECT 1"
```

**Error de encriptación:**
```bash
# Verificar estado
python verify_encryption.py
```

**Lentitud en consultas:**
```bash
# Verificar índices
python test_performance.py
```

---

## Conclusión

ClinicalLabManager es un sistema robusto y seguro para la gestión completa de laboratorios clínicos, implementando las mejores prácticas de:
- Transacciones ACID
- Optimización con índices
- Encriptación de datos sensibles
- Trazabilidad completa
- Validaciones automáticas
- Estadísticas optimizadas

**Ideal para laboratorios que requieren:**
- Seguridad de datos de pacientes
- Trazabilidad completa de operaciones
- Alertas de valores anormales
- Reportes y estadísticas detalladas
- Cumplimiento de normativas de privacidad de datos