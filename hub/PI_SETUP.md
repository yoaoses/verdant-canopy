# Verdant Canopy — Setup Raspberry Pi 4B

Instalación paso a paso del hub central.

---

## Pre-requisitos

```
✅ Pi 4B con Ubuntu 24.04 Server instalado
✅ Conexión ethernet a router
✅ Acceso SSH
✅ Usuario: canopyadmin
```

---

## Paso 1: Conexión SSH

Desde tu PC:

```bash
# Encontrar IP de la Pi en la red
ip a  # o ifconfig

# Conectar por SSH
ssh canopyadmin@192.168.X.X  # reemplazar con IP real

# Si es primera vez, aceptar fingerprint
# Ingresar password
```

Una vez dentro de la Pi:

```bash
# Verificar sistema
uname -a
# Debe mostrar: Linux ... 6.8.0-... aarch64 aarch64 aarch64 GNU/Linux

# Verificar Ubuntu
lsb_release -a
# Debe mostrar: Ubuntu 24.04.X LTS
```

---

## Paso 2: Actualizar Sistema Base

```bash
# Update repositories
sudo apt update

# Upgrade packages
sudo apt upgrade -y

# Instalar herramientas base
sudo apt install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    net-tools \
    python3-pip \
    python3-venv \
    build-essential

# Verificar Python
python3 --version
# Debe ser Python 3.12.x
```

---

## Paso 3: Configurar Swap (seguridad con 2GB RAM)

```bash
# Crear archivo swap de 1GB
sudo fallocate -l 1G /swapfile

# Permisos correctos
sudo chmod 600 /swapfile

# Formatear como swap
sudo mkswap /swapfile

# Activar swap
sudo swapon /swapfile

# Verificar
free -h
# Debe mostrar Swap: 1.0G

# Hacer permanente
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Ajustar swappiness (opcional)
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

---

## Paso 4: Instalar Mosquitto (MQTT Broker)

```bash
# Instalar
sudo apt install -y mosquitto mosquitto-clients

# Habilitar en boot
sudo systemctl enable mosquitto

# Iniciar
sudo systemctl start mosquitto

# Verificar status
sudo systemctl status mosquitto
# Debe mostrar: active (running)

# Test básico
mosquitto_sub -h localhost -t test &
mosquitto_pub -h localhost -t test -m "hello"
# Debe imprimir "hello"
```

**Configuración básica:**

```bash
# Backup config original
sudo cp /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.bak

# Editar config
sudo nano /etc/mosquitto/mosquitto.conf

# Agregar al final:
listener 1883 0.0.0.0
allow_anonymous true
max_queued_messages 1000
persistence true
persistence_location /var/lib/mosquitto/

# Guardar: Ctrl+O, Enter, Ctrl+X

# Reiniciar
sudo systemctl restart mosquitto

# Verificar puerto
sudo netstat -tlnp | grep 1883
# Debe mostrar: tcp ... 0.0.0.0:1883 ... mosquitto
```

---

## Paso 5: Clonar Repositorio

```bash
# Ir a home
cd ~

# Clonar repo
git clone git@github.com:yoaoses/verdant-canopy.git

# Si no tienes SSH key configurada:
git clone https://github.com/yoaoses/verdant-canopy.git

# Verificar
cd verdant-canopy
ls -la
# Debe mostrar: hub/ firmware/ pwa/ functions/ docs/
```

---

## Paso 6: Setup Python Virtual Environment

```bash
cd ~/verdant-canopy/hub

# Crear venv
python3 -m venv venv

# Activar
source venv/bin/activate

# Debería aparecer (venv) en el prompt

# Crear requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.109.2
uvicorn[standard]==0.27.1
python-multipart==0.0.9
pydantic==2.6.1
pydantic-settings==2.1.0

sqlalchemy==2.0.25
alembic==1.13.1

paho-mqtt==1.6.1

firebase-admin==6.4.0

python-dotenv==1.0.1
EOF

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Verificar instalación
python -c "import fastapi; print(fastapi.__version__)"
python -c "import paho.mqtt.client as mqtt; print('MQTT OK')"
```

---

## Paso 7: Inicializar Base de Datos SQLite

```bash
# Crear estructura de directorios
mkdir -p app/db
mkdir -p app/mqtt
mkdir -p app/api
mkdir -p app/firebase
mkdir -p app/utils
mkdir -p data

# Copiar schema SQL al proyecto
# (asumiendo que tienes DATABASE_SCHEMA.md en docs/)

# Crear script para inicializar DB
cat > init_db.py << 'EOF'
import sqlite3
from pathlib import Path

DB_PATH = Path("data/verdant.db")

schema = """
-- Schema completo aquí
-- Por ahora una versión simplificada

CREATE TABLE IF NOT EXISTS espacios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    ancho_cm REAL NOT NULL,
    largo_cm REAL NOT NULL,
    alto_cm REAL NOT NULL,
    ubicacion TEXT,
    creado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sensores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    espacio_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    nombre TEXT NOT NULL,
    pos_x_cm REAL NOT NULL,
    pos_y_cm REAL NOT NULL,
    pos_z_cm REAL NOT NULL,
    metadata_json TEXT,
    FOREIGN KEY (espacio_id) REFERENCES espacios(id)
);

CREATE TABLE IF NOT EXISTS zonas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    espacio_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    perfil_cultivo_id TEXT NOT NULL,
    vol_x_min REAL DEFAULT 0,
    vol_y_min REAL DEFAULT 0,
    vol_z_min REAL DEFAULT 0,
    vol_x_max REAL,
    vol_y_max REAL,
    vol_z_max REAL,
    estado TEXT DEFAULT 'activa',
    fecha_inicio DATE DEFAULT (DATE('now')),
    fecha_fin DATE,
    FOREIGN KEY (espacio_id) REFERENCES espacios(id)
);

CREATE TABLE IF NOT EXISTS lecturas_sensores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    zona_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_medicion TEXT NOT NULL,
    valor REAL NOT NULL,
    unidad TEXT NOT NULL,
    synced BOOLEAN DEFAULT 0,
    FOREIGN KEY (sensor_id) REFERENCES sensores(id),
    FOREIGN KEY (zona_id) REFERENCES zonas(id)
);

CREATE INDEX IF NOT EXISTS idx_lecturas_timestamp ON lecturas_sensores(timestamp);
CREATE INDEX IF NOT EXISTS idx_lecturas_synced ON lecturas_sensores(synced) WHERE synced = 0;

CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zona_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo TEXT NOT NULL,
    pos_x_cm REAL,
    pos_y_cm REAL,
    descripcion TEXT NOT NULL,
    payload_json TEXT,
    fotos_json TEXT,
    usuario_id TEXT,
    synced BOOLEAN DEFAULT 0,
    FOREIGN KEY (zona_id) REFERENCES zonas(id)
);

CREATE INDEX IF NOT EXISTS idx_eventos_timestamp ON eventos(timestamp DESC);
"""

def init_database():
    DB_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.executescript(schema)
    
    # Insertar datos de prueba
    cursor.execute("""
        INSERT INTO espacios (nombre, ancho_cm, largo_cm, alto_cm, ubicacion)
        VALUES ('Indoor Principal', 100, 100, 200, 'Valdivia, Chile')
    """)
    
    cursor.execute("""
        INSERT INTO zonas (espacio_id, nombre, perfil_cultivo_id, vol_x_max, vol_y_max, vol_z_max)
        VALUES (1, 'Zona 1', 'cannabis_indoor', 90, 90, 180)
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Base de datos inicializada en {DB_PATH}")
    print(f"   Espacio: Indoor Principal (100×100×200 cm)")
    print(f"   Zona 1 creada")

if __name__ == "__main__":
    init_database()
EOF

# Ejecutar
python init_db.py

# Verificar
sqlite3 data/verdant.db "SELECT * FROM espacios;"
# Debe mostrar: 1|Indoor Principal|100.0|100.0|200.0|Valdivia, Chile|...
```

---

## Paso 8: Crear FastAPI App Básica

```bash
# Crear app/main.py
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from datetime import datetime

app = FastAPI(title="Verdant Canopy API", version="0.1.0")

# CORS para PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "data/verdant.db"

@app.get("/")
def root():
    return {
        "name": "Verdant Canopy API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/zones")
def get_zones():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM zonas WHERE estado = 'activa'")
    zones = cursor.fetchall()
    conn.close()
    return {"zones": zones}

@app.get("/sensors/latest")
def get_latest_sensors(zone_id: int = 1):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM lecturas_sensores 
        WHERE zona_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 10
    """, (zone_id,))
    
    readings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"readings": readings}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Test manual
python app/main.py &
# Debe mostrar: INFO: Uvicorn running on http://0.0.0.0:8000

# Test desde otra terminal
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/zones

# Matar proceso
pkill -f uvicorn
```

---

## Paso 9: Crear Systemd Service

```bash
# Crear servicio para FastAPI
sudo nano /etc/systemd/system/verdant-api.service

# Contenido:
[Unit]
Description=Verdant Canopy FastAPI
After=network.target mosquitto.service

[Service]
Type=simple
User=yoaoses
WorkingDirectory=/home/yoaoses/verdant-canopy/hub
Environment="PATH=/home/yoaoses/verdant-canopy/hub/venv/bin"
ExecStart=/home/yoaoses/verdant-canopy/hub/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Guardar y salir

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicio
sudo systemctl enable verdant-api

# Iniciar servicio
sudo systemctl start verdant-api

# Verificar status
sudo systemctl status verdant-api

# Ver logs
sudo journalctl -u verdant-api -f
```

---

## Paso 10: Crear Cliente MQTT

```bash
# Crear app/mqtt/client.py
mkdir -p app/mqtt

cat > app/mqtt/client.py << 'EOF'
import paho.mqtt.client as mqtt
import json
import sqlite3
from datetime import datetime

DB_PATH = "data/verdant.db"

def on_connect(client, userdata, flags, rc):
    print(f"📡 Conectado a MQTT broker (rc: {rc})")
    client.subscribe("verdant/#")

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        
        print(f"📥 [{topic}] {payload}")
        
        # Guardar en SQLite
        if "sensors" in topic:
            save_sensor_reading(payload)
        
    except Exception as e:
        print(f"❌ Error procesando mensaje: {e}")

def save_sensor_reading(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Insertar cada sensor como fila
    for key, value in data.items():
        if key == "timestamp":
            continue
        
        cursor.execute("""
            INSERT INTO lecturas_sensores 
            (sensor_id, zona_id, timestamp, tipo_medicion, valor, unidad, synced)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (1, 1, datetime.now(), key, value, "", 0))
    
    conn.commit()
    conn.close()
    print(f"✅ Guardado en SQLite")

def start_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect("localhost", 1883, 60)
    
    print("🚀 Cliente MQTT iniciado")
    client.loop_forever()

if __name__ == "__main__":
    start_mqtt_client()
EOF

# Test manual
cd ~/verdant-canopy/hub
source venv/bin/activate
python app/mqtt/client.py &

# En otra terminal, publicar test
mosquitto_pub -h localhost -t verdant/zone1/sensors -m '{"temperatura":24.5,"luz_lux":18000}'

# Verificar en SQLite
sqlite3 data/verdant.db "SELECT * FROM lecturas_sensores ORDER BY timestamp DESC LIMIT 5;"

# Matar proceso
pkill -f mqtt/client
```

---

## Paso 11: Crear Servicio MQTT

```bash
sudo nano /etc/systemd/system/verdant-mqtt.service

# Contenido:
[Unit]
Description=Verdant Canopy MQTT Client
After=network.target mosquitto.service

[Service]
Type=simple
User=yoaoses
WorkingDirectory=/home/yoaoses/verdant-canopy/hub
Environment="PATH=/home/yoaoses/verdant-canopy/hub/venv/bin"
ExecStart=/home/yoaoses/verdant-canopy/hub/venv/bin/python app/mqtt/client.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Guardar

sudo systemctl daemon-reload
sudo systemctl enable verdant-mqtt
sudo systemctl start verdant-mqtt
sudo systemctl status verdant-mqtt
```

---

## Paso 12: Verificar Todo Funcionando

```bash
# Status de todos los servicios
sudo systemctl status mosquitto
sudo systemctl status verdant-api
sudo systemctl status verdant-mqtt

# Test completo end-to-end
# 1. Publicar mensaje MQTT
mosquitto_pub -h localhost -t verdant/zone1/sensors -m '{"temperatura":25.0,"humedad":60,"luz_lux":20000}'

# 2. Ver que llegó al cliente MQTT
sudo journalctl -u verdant-mqtt -n 20

# 3. Ver que se guardó en SQLite
sqlite3 ~/verdant-canopy/hub/data/verdant.db "SELECT * FROM lecturas_sensores ORDER BY timestamp DESC LIMIT 5;"

# 4. Ver que FastAPI lo expone
curl http://localhost:8000/sensors/latest
```

---

## Resumen de Servicios

```
┌────────────────────────────────────┐
│  Servicios corriendo en Pi 4B      │
├────────────────────────────────────┤
│  mosquitto      :1883              │
│  verdant-api    :8000              │
│  verdant-mqtt   (subscriber)       │
└────────────────────────────────────┘

Logs:
sudo journalctl -u mosquitto -f
sudo journalctl -u verdant-api -f
sudo journalctl -u verdant-mqtt -f

Reiniciar:
sudo systemctl restart mosquitto
sudo systemctl restart verdant-api
sudo systemctl restart verdant-mqtt
```

---

## Próximos Pasos

1. ✅ Hub funcionando localmente
2. ⬜ Conectar Pico W (cargar firmware con mocks)
3. ⬜ Verificar datos fluyendo Pico W → MQTT → SQLite
4. ⬜ Crear Firebase project
5. ⬜ Implementar sync SQLite → Firebase
6. ⬜ Crear PWA básica

---

**La Pi está lista para recibir datos del Pico W.**

Siguiente paso: Cargar firmware en el Pico W con los mocks actualizados.
