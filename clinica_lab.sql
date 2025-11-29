-- Conectarse a PostgreSQL
psql -U postgres

CREATE DATABASE clinica_lab;
\c clinica_lab

-- REQUISITO 3: Tabla con encriptación
CREATE TABLE pacientes (
    id SERIAL PRIMARY KEY,
    nombre_enc BYTEA NOT NULL,
    dni_enc BYTEA UNIQUE NOT NULL,
    fecha_nacimiento DATE,
    telefono_enc BYTEA,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- REQUISITO 2: Índices
CREATE INDEX idx_pacientes_created ON pacientes(created_at);

-- Tipos de análisis con rangos normales
CREATE TABLE tipos_analisis (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    valor_min NUMERIC(10,2),
    valor_max NUMERIC(10,2),
    unidad VARCHAR(20)
);

-- REQUISITO 2: Índices
CREATE INDEX idx_tipos_codigo ON tipos_analisis(codigo);
CREATE INDEX idx_tipos_nombre ON tipos_analisis(nombre);

-- Órdenes de análisis
CREATE TABLE ordenes (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER REFERENCES pacientes(id),
    fecha_orden TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'PENDIENTE',
    usuario_crea VARCHAR(50) NOT NULL
);

-- REQUISITO 2: Índices para optimizar consultas
CREATE INDEX idx_ordenes_paciente ON ordenes(paciente_id);
CREATE INDEX idx_ordenes_fecha ON ordenes(fecha_orden DESC);
CREATE INDEX idx_ordenes_estado ON ordenes(estado);

-- Resultados de análisis
CREATE TABLE resultados (
    id SERIAL PRIMARY KEY,
    orden_id INTEGER REFERENCES ordenes(id),
    tipo_analisis_id INTEGER REFERENCES tipos_analisis(id),
    valor NUMERIC(10,2),
    fecha_resultado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_carga VARCHAR(50),
    fuera_rango BOOLEAN DEFAULT FALSE
);

-- REQUISITO 2: Índices
CREATE INDEX idx_resultados_orden ON resultados(orden_id);
CREATE INDEX idx_resultados_tipo ON resultados(tipo_analisis_id);
CREATE INDEX idx_resultados_fecha ON resultados(fecha_resultado DESC);

-- REQUISITO 4: Tabla de auditoría
CREATE TABLE auditoria_accesos (
    id SERIAL PRIMARY KEY,
    tabla VARCHAR(50) NOT NULL,
    registro_id INTEGER NOT NULL,
    accion VARCHAR(20) NOT NULL,
    usuario VARCHAR(50) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    detalles TEXT
);

-- REQUISITO 2: Índices para auditoría
CREATE INDEX idx_auditoria_fecha ON auditoria_accesos(fecha DESC);
CREATE INDEX idx_auditoria_usuario ON auditoria_accesos(usuario);
CREATE INDEX idx_auditoria_tabla ON auditoria_accesos(tabla, registro_id);

-- Datos de prueba
INSERT INTO tipos_analisis (codigo, nombre, valor_min, valor_max, unidad) VALUES
('HEM', 'Hemograma Completo', 4.5, 5.5, 'mill/μL'),
('GLU', 'Glucosa en Sangre', 70, 100, 'mg/dL'),
('COL', 'Colesterol Total', 0, 200, 'mg/dL'),
('TRI', 'Triglicéridos', 0, 150, 'mg/dL'),
('CRE', 'Creatinina', 0.6, 1.2, 'mg/dL');
