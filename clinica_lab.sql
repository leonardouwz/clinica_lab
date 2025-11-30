-- ============================================
-- BASE DE DATOS
-- ============================================
CREATE DATABASE clinica_lab;
\c clinica_lab;

-- ============================================
-- TABLA: PACIENTES
-- ============================================
CREATE TABLE pacientes (
    id SERIAL PRIMARY KEY,
    nombre_enc BYTEA NOT NULL,
    dni_enc BYTEA UNIQUE NOT NULL,
    fecha_nacimiento DATE,
    telefono_enc BYTEA,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Validación mínima
    CONSTRAINT chk_fecha_nac CHECK (fecha_nacimiento IS NULL OR fecha_nacimiento < CURRENT_DATE)
);

-- Índices
CREATE INDEX idx_pacientes_created ON pacientes(created_at DESC);


-- ============================================
-- TABLA: TIPOS DE ANALISIS
-- ============================================
CREATE TABLE tipos_analisis (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    valor_min NUMERIC(10,2),
    valor_max NUMERIC(10,2),
    unidad VARCHAR(20),

    -- Rango válido
    CONSTRAINT chk_rangos_normales CHECK (
        valor_min IS NULL OR valor_max IS NULL OR valor_min <= valor_max
    )
);

CREATE INDEX idx_tipos_codigo ON tipos_analisis(codigo);
CREATE INDEX idx_tipos_nombre ON tipos_analisis(nombre);


-- ============================================
-- TABLA: ORDENES
-- ============================================
CREATE TABLE ordenes (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    fecha_orden TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'PENDIENTE',
    usuario_crea VARCHAR(50) NOT NULL,

    CONSTRAINT chk_estado CHECK (estado IN ('PENDIENTE', 'EN PROCESO', 'COMPLETADO'))
);

CREATE INDEX idx_ordenes_paciente ON ordenes(paciente_id);
CREATE INDEX idx_ordenes_fecha ON ordenes(fecha_orden DESC);
CREATE INDEX idx_ordenes_estado ON ordenes(estado);


-- ============================================
-- TABLA: RESULTADOS
-- ============================================
CREATE TABLE resultados (
    id SERIAL PRIMARY KEY,
    orden_id INTEGER NOT NULL REFERENCES ordenes(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    tipo_analisis_id INTEGER NOT NULL REFERENCES tipos_analisis(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    valor NUMERIC(10,2),
    fecha_resultado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_carga VARCHAR(50),
    fuera_rango BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_resultados_orden ON resultados(orden_id);
CREATE INDEX idx_resultados_tipo ON resultados(tipo_analisis_id);
CREATE INDEX idx_resultados_fecha ON resultados(fecha_resultado DESC);


-- ============================================
-- TABLA DE AUDITORÍA
-- ============================================
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

CREATE INDEX idx_auditoria_fecha ON auditoria_accesos(fecha DESC);
CREATE INDEX idx_auditoria_usuario ON auditoria_accesos(usuario);
CREATE INDEX idx_auditoria_tabla ON auditoria_accesos(tabla, registro_id);


-- ============================================
-- FUNCION DE AUDITORIA   
-- ============================================
CREATE OR REPLACE FUNCTION registrar_auditoria()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO auditoria_accesos(tabla, registro_id, accion, usuario, detalles)
    VALUES (
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        CURRENT_USER,
        'Cambio automático por trigger'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ============================================
-- TRIGGERS (opcionales pero recomendados)
-- ============================================

CREATE TRIGGER trg_auditar_pacientes
AFTER INSERT OR UPDATE OR DELETE ON pacientes
FOR EACH ROW EXECUTE FUNCTION registrar_auditoria();

CREATE TRIGGER trg_auditar_ordenes
AFTER INSERT OR UPDATE OR DELETE ON ordenes
FOR EACH ROW EXECUTE FUNCTION registrar_auditoria();

CREATE TRIGGER trg_auditar_resultados
AFTER INSERT OR UPDATE OR DELETE ON resultados
FOR EACH ROW EXECUTE FUNCTION registrar_auditoria();


-- ============================================
-- DATOS DE PRUEBA
-- ============================================
INSERT INTO tipos_analisis (codigo, nombre, valor_min, valor_max, unidad) VALUES
('HEM', 'Hemograma Completo', 4.5, 5.5, 'mill/μL'),
('GLU', 'Glucosa en Sangre', 70, 100, 'mg/dL'),
('COL', 'Colesterol Total', 0, 200, 'mg/dL'),
('TRI', 'Triglicéridos', 0, 150, 'mg/dL'),
('CRE', 'Creatinina', 0.6, 1.2, 'mg/dL');
