# Verdant Canopy — Database Schema

Modelo de datos completo basado en geometría espacial y densidad de masa verde.

---

## Diagrama Entidad-Relación

```
┌─────────────────────────────────────────────────────────┐
│                      ESPACIOS                            │
│  PK: id                                                  │
│  ────────────────────────────────────────────────────   │
│  nombre: TEXT                                            │
│  ancho_cm: REAL                                          │
│  largo_cm: REAL                                          │
│  alto_cm: REAL                                           │
│  ubicacion: TEXT                                         │
│  creado_at: TIMESTAMP                                    │
└───────────────┬─────────────────────────────────────────┘
                │
                │ 1:N
                ▼
┌─────────────────────────────────────────────────────────┐
│                       SENSORES                           │
│  PK: id                                                  │
│  FK: espacio_id                                          │
│  ────────────────────────────────────────────────────   │
│  tipo: TEXT (rcwl, dht22, bh1750, etc)                  │
│  nombre: TEXT                                            │
│  pos_x_cm: REAL                                          │
│  pos_y_cm: REAL                                          │
│  pos_z_cm: REAL                                          │
│  metadata_json: TEXT                                     │
└───────────────┬─────────────────────────────────────────┘
                │
                │ 1:N
                ▼
┌─────────────────────────────────────────────────────────┐
│                  LECTURAS_SENSORES                       │
│  PK: id                                                  │
│  FK: sensor_id, zona_id                                  │
│  ────────────────────────────────────────────────────   │
│  timestamp: TIMESTAMP                                    │
│  tipo_medicion: TEXT                                     │
│  valor: REAL                                             │
│  unidad: TEXT                                            │
│  synced: BOOLEAN                                         │
└──────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────┐
│                        ZONAS                             │
│  PK: id                                                  │
│  FK: espacio_id                                          │
│  ────────────────────────────────────────────────────   │
│  nombre: TEXT                                            │
│  perfil_cultivo_id: TEXT                                 │
│  vol_x_min, vol_y_min, vol_z_min: REAL                  │
│  vol_x_max, vol_y_max, vol_z_max: REAL                  │
│  volumen_total_cm3: REAL                                 │
│  estado: TEXT (activa, inactiva)                         │
│  fecha_inicio, fecha_fin: DATE                           │
└───────────┬───────────────┬─────────────────────────────┘
            │               │
            │ 1:N           │ 1:N
            ▼               ▼
┌───────────────────┐  ┌──────────────────────────────────┐
│  MAPAS_DENSIDAD   │  │          EVENTOS                 │
│  PK: id           │  │  PK: id                          │
│  FK: zona_id      │  │  FK: zona_id                     │
│  ─────────────    │  │  ────────────────────────────    │
│  timestamp        │  │  timestamp: TIMESTAMP            │
│  volumen_ocupado  │  │  tipo: TEXT                      │
│  pct_ocupacion    │  │  pos_x_cm, pos_y_cm: REAL       │
│  altura_max       │  │  descripcion: TEXT               │
│  altura_promedio  │  │  payload_json: TEXT              │
│  altura_min       │  │  fotos_json: TEXT                │
│  uniformidad      │  │  usuario_id: TEXT                │
│  centro_x,y,z     │  │  synced: BOOLEAN                 │
│  grid_data_json   │  └──────────────────────────────────┘
└───────────────────┘
            │
            │ 1:N
            ▼
┌──────────────────────────────────────────────────────────┐
│              CONFIGURACION_ACTIVA                         │
│  PK: id                                                   │
│  FK: zona_id                                              │
│  ─────────────────────────────────────────────────────   │
│  fecha: DATE                                              │
│  luz_json: TEXT                                           │
│  ventilacion_json: TEXT                                   │
│  costo_kwh: REAL                                          │
│  horas_activas: REAL                                      │
│  UNIQUE(zona_id, fecha)                                   │
└───────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────┐
│                      COSECHAS                             │
│  PK: id                                                   │
│  FK: zona_id                                              │
│  ─────────────────────────────────────────────────────   │
│  timestamp: TIMESTAMP                                     │
│  peso_humedo: REAL                                        │
│  peso_seco: REAL                                          │
│  unidad: TEXT (g, kg)                                     │
│  notas: TEXT                                              │
│  costo_total_ciclo: REAL                                  │
└───────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────┐
│                  PERFILES_CULTIVO                         │
│  PK: id (TEXT)                                            │
│  ─────────────────────────────────────────────────────   │
│  nombre: TEXT                                             │
│  config_json: TEXT                                        │
│  creado_at: TIMESTAMP                                     │
│                                                           │
│  Referenciado por: zonas.perfil_cultivo_id               │
└───────────────────────────────────────────────────────────┘
```

---

## Relaciones y Cardinalidad

| Entidad Padre | Relación | Entidad Hija | Cardinalidad |
|--------------|----------|--------------|--------------|
| ESPACIOS | tiene | SENSORES | 1:N |
| ESPACIOS | contiene | ZONAS | 1:N |
| SENSORES | genera | LECTURAS_SENSORES | 1:N |
| ZONAS | tiene | MAPAS_DENSIDAD | 1:N |
| ZONAS | registra | EVENTOS | 1:N |
| ZONAS | configura | CONFIGURACION_ACTIVA | 1:N |
| ZONAS | produce | COSECHAS | 1:N |
| PERFILES_CULTIVO | define | ZONAS | 1:N |

---

## Schema SQL Completo

```sql
-- ==========================================
-- CONFIGURACIÓN DEL ESPACIO FÍSICO
-- ==========================================

CREATE TABLE espacios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    ancho_cm REAL NOT NULL CHECK(ancho_cm > 0),
    largo_cm REAL NOT NULL CHECK(largo_cm > 0),
    alto_cm REAL NOT NULL CHECK(alto_cm > 0),
    ubicacion TEXT,
    creado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sensores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    espacio_id INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN (
        'rcwl', 'dht22', 'ds18b20', 'bh1750', 
        'mhz19b', 'ph', 'tds', 'pt100'
    )),
    nombre TEXT NOT NULL,
    pos_x_cm REAL NOT NULL,
    pos_y_cm REAL NOT NULL,
    pos_z_cm REAL NOT NULL,
    metadata_json TEXT,
    FOREIGN KEY (espacio_id) REFERENCES espacios(id) ON DELETE CASCADE
);

CREATE INDEX idx_sensores_espacio ON sensores(espacio_id);
CREATE INDEX idx_sensores_tipo ON sensores(tipo);

-- ==========================================
-- ZONAS DE CULTIVO
-- ==========================================

CREATE TABLE zonas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    espacio_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    perfil_cultivo_id TEXT NOT NULL,
    
    -- Bounding box del volumen cultivable
    vol_x_min REAL NOT NULL DEFAULT 0,
    vol_y_min REAL NOT NULL DEFAULT 0,
    vol_z_min REAL NOT NULL DEFAULT 0,
    vol_x_max REAL NOT NULL,
    vol_y_max REAL NOT NULL,
    vol_z_max REAL NOT NULL,
    
    -- Volumen total (calculado)
    volumen_total_cm3 REAL GENERATED ALWAYS AS (
        (vol_x_max - vol_x_min) * 
        (vol_y_max - vol_y_min) * 
        (vol_z_max - vol_z_min)
    ) STORED,
    
    estado TEXT NOT NULL DEFAULT 'activa' 
        CHECK(estado IN ('activa', 'inactiva', 'finalizada')),
    fecha_inicio DATE NOT NULL DEFAULT (DATE('now')),
    fecha_fin DATE,
    
    FOREIGN KEY (espacio_id) REFERENCES espacios(id) ON DELETE CASCADE,
    FOREIGN KEY (perfil_cultivo_id) REFERENCES perfiles_cultivo(id),
    
    CHECK(vol_x_max > vol_x_min),
    CHECK(vol_y_max > vol_y_min),
    CHECK(vol_z_max > vol_z_min),
    CHECK(fecha_fin IS NULL OR fecha_fin >= fecha_inicio)
);

CREATE INDEX idx_zonas_espacio ON zonas(espacio_id);
CREATE INDEX idx_zonas_estado ON zonas(estado);
CREATE INDEX idx_zonas_perfil ON zonas(perfil_cultivo_id);

-- ==========================================
-- PERFILES DE CULTIVO
-- ==========================================

CREATE TABLE perfiles_cultivo (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    config_json TEXT NOT NULL,
    creado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK(json_valid(config_json))
);

-- Insertar perfiles predefinidos
INSERT INTO perfiles_cultivo (id, nombre, config_json) VALUES 
('cannabis_indoor', 'Cannabis Indoor Medicinal', '{
    "tipo_organismo": "planta",
    "metricas": {
        "ambiente": ["temperatura", "humedad", "luz_dli", "co2"],
        "agua": ["ph", "tds", "volumen_ml"]
    },
    "umbrales": {
        "temp_min": 18, "temp_max": 28,
        "humedad_min": 40, "humedad_max": 70,
        "ph_min": 6.0, "ph_max": 7.0
    },
    "fases": [
        {"nombre": "germinacion", "dias": 7},
        {"nombre": "crecimiento", "dias": 30},
        {"nombre": "floracion", "dias": 60}
    ],
    "luz_por_fase": {
        "crecimiento": "18/6",
        "floracion": "12/12"
    }
}'),
('lechuga_hidro', 'Lechuga Hidropónica', '{
    "tipo_organismo": "planta",
    "metricas": {
        "ambiente": ["temperatura", "humedad", "luz_dli"]
    },
    "umbrales": {
        "temp_min": 15, "temp_max": 25,
        "humedad_min": 50, "humedad_max": 70
    }
}'),
('hongos_ostra', 'Hongos Ostra', '{
    "tipo_organismo": "hongo",
    "metricas": {
        "ambiente": ["temperatura", "humedad", "co2"]
    },
    "umbrales": {
        "temp_min": 18, "temp_max": 24,
        "humedad_min": 80, "humedad_max": 95
    }
}'),
('experimental', 'Cultivo Experimental', '{
    "tipo_organismo": "desconocido",
    "metricas": {"ambiente": ["temperatura", "humedad", "luz"]},
    "umbrales": {},
    "notas": "Para cultivos sin datos históricos"
}');

-- ==========================================
-- LECTURAS DE SENSORES
-- ==========================================

CREATE TABLE lecturas_sensores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    zona_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    tipo_medicion TEXT NOT NULL,
    valor REAL NOT NULL,
    unidad TEXT NOT NULL,
    
    synced BOOLEAN DEFAULT 0,
    
    FOREIGN KEY (sensor_id) REFERENCES sensores(id) ON DELETE CASCADE,
    FOREIGN KEY (zona_id) REFERENCES zonas(id) ON DELETE SET NULL
);

CREATE INDEX idx_lecturas_timestamp ON lecturas_sensores(timestamp);
CREATE INDEX idx_lecturas_sensor ON lecturas_sensores(sensor_id);
CREATE INDEX idx_lecturas_zona ON lecturas_sensores(zona_id);
CREATE INDEX idx_lecturas_synced ON lecturas_sensores(synced) WHERE synced = 0;

-- ==========================================
-- MAPAS DE DENSIDAD ESPACIAL
-- ==========================================

CREATE TABLE mapas_densidad (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zona_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Métricas de masa verde
    volumen_ocupado_cm3 REAL NOT NULL,
    porcentaje_ocupacion REAL GENERATED ALWAYS AS (
        (volumen_ocupado_cm3 * 100.0) / 
        (SELECT volumen_total_cm3 FROM zonas WHERE id = zona_id)
    ) STORED,
    
    altura_max_cm REAL NOT NULL,
    altura_promedio_cm REAL NOT NULL,
    altura_min_cm REAL NOT NULL,
    uniformidad_cm REAL NOT NULL,
    
    -- Centro de masa
    centro_x_cm REAL,
    centro_y_cm REAL,
    centro_z_cm REAL,
    
    -- Grid 3D (opcional)
    grid_resolucion_cm INTEGER DEFAULT 10,
    grid_data_json TEXT,
    
    FOREIGN KEY (zona_id) REFERENCES zonas(id) ON DELETE CASCADE,
    
    CHECK(volumen_ocupado_cm3 >= 0),
    CHECK(altura_max_cm >= altura_min_cm),
    CHECK(uniformidad_cm >= 0)
);

CREATE INDEX idx_mapas_zona ON mapas_densidad(zona_id);
CREATE INDEX idx_mapas_timestamp ON mapas_densidad(timestamp DESC);

-- ==========================================
-- EVENTOS DEL USUARIO
-- ==========================================

CREATE TABLE eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zona_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    tipo TEXT NOT NULL CHECK(tipo IN (
        'siembra', 'trasplante', 'poda', 'riego', 
        'fertilizacion', 'observacion', 'ajuste_luz',
        'ajuste_ventilacion', 'cosecha_parcial', 'otro'
    )),
    
    -- Ubicación opcional
    pos_x_cm REAL,
    pos_y_cm REAL,
    
    descripcion TEXT NOT NULL,
    payload_json TEXT,
    fotos_json TEXT,
    usuario_id TEXT,
    
    synced BOOLEAN DEFAULT 0,
    
    FOREIGN KEY (zona_id) REFERENCES zonas(id) ON DELETE CASCADE,
    
    CHECK(payload_json IS NULL OR json_valid(payload_json)),
    CHECK(fotos_json IS NULL OR json_valid(fotos_json))
);

CREATE INDEX idx_eventos_zona ON eventos(zona_id);
CREATE INDEX idx_eventos_timestamp ON eventos(timestamp DESC);
CREATE INDEX idx_eventos_tipo ON eventos(tipo);
CREATE INDEX idx_eventos_synced ON eventos(synced) WHERE synced = 0;

-- ==========================================
-- CONFIGURACIÓN ACTIVA
-- ==========================================

CREATE TABLE configuracion_activa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zona_id INTEGER NOT NULL,
    fecha DATE NOT NULL DEFAULT (DATE('now')),
    
    luz_json TEXT,
    ventilacion_json TEXT,
    
    costo_kwh REAL,
    horas_activas REAL,
    
    FOREIGN KEY (zona_id) REFERENCES zonas(id) ON DELETE CASCADE,
    
    UNIQUE(zona_id, fecha),
    
    CHECK(luz_json IS NULL OR json_valid(luz_json)),
    CHECK(ventilacion_json IS NULL OR json_valid(ventilacion_json)),
    CHECK(costo_kwh IS NULL OR costo_kwh >= 0),
    CHECK(horas_activas IS NULL OR (horas_activas >= 0 AND horas_activas <= 24))
);

CREATE INDEX idx_config_zona_fecha ON configuracion_activa(zona_id, fecha DESC);

-- ==========================================
-- COSECHAS
-- ==========================================

CREATE TABLE cosechas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zona_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    peso_humedo REAL,
    peso_seco REAL NOT NULL,
    unidad TEXT NOT NULL CHECK(unidad IN ('g', 'kg')),
    
    notas TEXT,
    costo_total_ciclo REAL,
    
    FOREIGN KEY (zona_id) REFERENCES zonas(id) ON DELETE CASCADE,
    
    CHECK(peso_seco > 0),
    CHECK(peso_humedo IS NULL OR peso_humedo >= peso_seco)
);

CREATE INDEX idx_cosechas_zona ON cosechas(zona_id);
CREATE INDEX idx_cosechas_timestamp ON cosechas(timestamp DESC);
```

---

## Triggers y Validaciones

```sql
-- Validar que sensores estén dentro del espacio
CREATE TRIGGER validar_posicion_sensor
BEFORE INSERT ON sensores
BEGIN
    SELECT RAISE(ABORT, 'Sensor fuera del espacio')
    WHERE NEW.pos_x_cm < 0 OR NEW.pos_x_cm > (SELECT ancho_cm FROM espacios WHERE id = NEW.espacio_id)
       OR NEW.pos_y_cm < 0 OR NEW.pos_y_cm > (SELECT largo_cm FROM espacios WHERE id = NEW.espacio_id)
       OR NEW.pos_z_cm < 0 OR NEW.pos_z_cm > (SELECT alto_cm FROM espacios WHERE id = NEW.espacio_id);
END;

-- Finalizar zona automáticamente al cosechar
CREATE TRIGGER finalizar_zona_cosecha
AFTER INSERT ON cosechas
WHEN NEW.notas LIKE '%final%' OR NEW.notas LIKE '%completa%'
BEGIN
    UPDATE zonas 
    SET estado = 'finalizada', 
        fecha_fin = DATE(NEW.timestamp)
    WHERE id = NEW.zona_id;
END;
```

---

## Vistas Útiles

```sql
-- Vista de estado actual por zona
CREATE VIEW v_estado_zonas AS
SELECT 
    z.id,
    z.nombre,
    z.estado,
    z.fecha_inicio,
    julianday('now') - julianday(z.fecha_inicio) as dias_activos,
    p.nombre as perfil,
    
    -- Último mapa de densidad
    m.volumen_ocupado_cm3,
    m.porcentaje_ocupacion,
    m.altura_promedio_cm,
    m.timestamp as ultima_medicion,
    
    -- Última configuración
    c.luz_json,
    c.ventilacion_json
    
FROM zonas z
LEFT JOIN perfiles_cultivo p ON p.id = z.perfil_cultivo_id
LEFT JOIN (
    SELECT zona_id, MAX(timestamp) as max_ts
    FROM mapas_densidad
    GROUP BY zona_id
) last_map ON last_map.zona_id = z.id
LEFT JOIN mapas_densidad m ON m.zona_id = z.id AND m.timestamp = last_map.max_ts
LEFT JOIN (
    SELECT zona_id, MAX(fecha) as max_fecha
    FROM configuracion_activa
    GROUP BY zona_id
) last_config ON last_config.zona_id = z.id
LEFT JOIN configuracion_activa c ON c.zona_id = z.id AND c.fecha = last_config.max_fecha;

-- Vista de crecimiento semanal
CREATE VIEW v_crecimiento_semanal AS
SELECT 
    zona_id,
    strftime('%Y-W%W', timestamp) as semana,
    AVG(volumen_ocupado_cm3) as vol_promedio,
    AVG(altura_promedio_cm) as altura_promedio,
    MIN(altura_min_cm) as altura_min,
    MAX(altura_max_cm) as altura_max
FROM mapas_densidad
GROUP BY zona_id, semana
ORDER BY zona_id, semana;
```

---

## Queries Comunes

```sql
-- Estado actual de todas las zonas activas
SELECT * FROM v_estado_zonas WHERE estado = 'activa';

-- Evolución del volumen ocupado
SELECT timestamp, volumen_ocupado_cm3, porcentaje_ocupacion
FROM mapas_densidad
WHERE zona_id = 1
ORDER BY timestamp;

-- Eventos agrupados por tipo
SELECT tipo, COUNT(*) as cantidad, MAX(timestamp) as ultimo
FROM eventos
WHERE zona_id = 1
GROUP BY tipo;

-- Costo acumulado de un ciclo
SELECT 
    zona_id,
    SUM(horas_activas * costo_kwh / 1000) as costo_total_pesos
FROM configuracion_activa
WHERE zona_id = 1
GROUP BY zona_id;

-- Tasa de crecimiento diaria
SELECT 
    DATE(timestamp) as fecha,
    AVG(altura_promedio_cm) as altura,
    AVG(altura_promedio_cm) - LAG(AVG(altura_promedio_cm)) OVER (ORDER BY DATE(timestamp)) as crecimiento_diario
FROM mapas_densidad
WHERE zona_id = 1
GROUP BY DATE(timestamp);
```

---

## Tamaño Estimado de Datos

| Tabla | Frecuencia | Registros/día | Registros/ciclo (90d) | Tamaño aprox |
|-------|-----------|---------------|----------------------|--------------|
| lecturas_sensores | 30s | 2,880 | 259,200 | ~50 MB |
| mapas_densidad | 6h | 4 | 360 | ~1 MB |
| eventos | manual | ~5 | 450 | ~500 KB |
| configuracion_activa | diaria | 1 | 90 | ~50 KB |

**Total por ciclo:** ~52 MB en SQLite

**Estrategia de limpieza:**
- Mantener últimos 7 días en detalle completo
- Agregar a promedios por hora después de 7 días
- Mantener histórico agregado indefinidamente
