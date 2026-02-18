# Verdant Canopy — Arquitectura del Sistema

Arquitectura completa desde sensores físicos hasta interfaz de usuario.

---

## Vista de Alto Nivel

```
┌──────────────────────────────────────────────────────────────────┐
│                         USUARIO FINAL                             │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  PWA en PC   │  │ PWA en Celular│  │ Tablet Kiosk │          │
│  │  Dashboard   │  │  4G / WiFi    │  │  WiFi local  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
          │ HTTPS            │ HTTPS            │ HTTP local
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CAPA NUBE                                │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    FIREBASE                               │  │
│  │                                                           │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │  Firestore  │  │ Cloud        │  │   Hosting      │  │  │
│  │  │  (NoSQL)    │  │ Functions    │  │   (PWA)        │  │  │
│  │  │             │  │ (Node.js)    │  │                │  │  │
│  │  │ - readings  │  │ - onWrite    │  │ - React build  │  │  │
│  │  │ - events    │  │   triggers   │  │ - Service      │  │  │
│  │  │ - zones     │  │ - FCM alerts │  │   Workers      │  │  │
│  │  └─────────────┘  └──────────────┘  └────────────────┘  │  │
│  │                                                           │  │
│  │  ┌─────────────┐  ┌──────────────┐                      │  │
│  │  │  Auth       │  │   FCM        │                      │  │
│  │  │  (Google)   │  │ (Push Web)   │                      │  │
│  │  └─────────────┘  └──────────────┘                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────┬────────────────────────────────────────────────────┘
              │
              │ Firebase Admin SDK
              │ onSnapshot (realtime)
              ▼
┌──────────────────────────────────────────────────────────────────┐
│                         CAPA HUB LOCAL                            │
│                    Raspberry Pi 4B (Ubuntu 24)                   │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                      SERVICIOS                              │  │
│  │                                                             │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
│  │  │  Mosquitto   │  │   FastAPI    │  │ Firebase        │  │  │
│  │  │  MQTT Broker │  │   HTTP API   │  │ Listener        │  │  │
│  │  │              │  │              │  │                 │  │  │
│  │  │ :1883        │  │ :8000        │  │ Python daemon   │  │  │
│  │  │              │  │              │  │ onSnapshot()    │  │  │
│  │  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘  │  │
│  │         │                 │                    │           │  │
│  │         └─────────────────┴────────────────────┘           │  │
│  │                           │                                │  │
│  │                           ▼                                │  │
│  │                  ┌─────────────────┐                       │  │
│  │                  │    SQLite       │                       │  │
│  │                  │    Database     │                       │  │
│  │                  │                 │                       │  │
│  │                  │  - espacios     │                       │  │
│  │                  │  - zonas        │                       │  │
│  │                  │  - sensores     │                       │  │
│  │                  │  - lecturas     │                       │  │
│  │                  │  - mapas        │                       │  │
│  │                  │  - eventos      │                       │  │
│  │                  └─────────────────┘                       │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                   SYNC SERVICE                              │  │
│  │                   Python daemon                             │  │
│  │                                                             │  │
│  │   Cada 5 min:                                               │  │
│  │   SQLite (pendientes) → Firebase (batch upload)             │  │
│  │                                                             │  │
│  │   En tiempo real:                                           │  │
│  │   Firebase commands → MQTT local                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                   WIFI HOTSPOT                              │  │
│  │   hostapd + dnsmasq                                         │  │
│  │   SSID: verdant-hub                                         │  │
│  │   192.168.4.1                                               │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────┬────────────────────────────────────────────────────┘
              │
              │ MQTT + WiFi local
              ▼
┌──────────────────────────────────────────────────────────────────┐
│                      CAPA EDGE (Sensores)                         │
│                                                                   │
│  ┌─────────────────────┐      ┌─────────────────────┐           │
│  │   Pico W #1         │      │   Pico W #2         │           │
│  │   Ambiente+Canopy   │      │   Agua (futuro)     │           │
│  │                     │      │                     │           │
│  │  ┌───────────────┐  │      │  ┌───────────────┐  │           │
│  │  │ MicroPython   │  │      │  │ MicroPython   │  │           │
│  │  │ Firmware      │  │      │  │ Firmware      │  │           │
│  │  └───────────────┘  │      │  └───────────────┘  │           │
│  │                     │      │                     │           │
│  │  Sensores:          │      │  Sensores:          │           │
│  │  • BH1750 (luz)     │      │  • PT100 (temp)     │           │
│  │  • DS18B20 (temp)   │      │  • pH probe         │           │
│  │  • RCWL-1601 ×4     │      │  • TDS meter        │           │
│  │    (canopy map)     │      │                     │           │
│  │                     │      │  Display:           │           │
│  │  Actuadores:        │      │  • OLED 128x32      │           │
│  │  • Relay Luz        │      │                     │           │
│  │  • Relay Extractor  │      │                     │           │
│  └─────────────────────┘      └─────────────────────┘           │
│                                                                   │
│  ┌─────────────────────┐                                         │
│  │   ESP8266 (opt)     │                                         │
│  │   Sensor adicional  │                                         │
│  │                     │                                         │
│  │  Solo publica MQTT  │                                         │
│  │  Sin failsafe       │                                         │
│  └─────────────────────┘                                         │
└───────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Datos — Lectura de Sensores

```
┌─────────────────────────────────────────────────────────────┐
│ 1. LECTURA (cada 30s)                                       │
│                                                              │
│    Pico W #1                                                │
│    ├─ BH1750.read()         → 18000 lux                    │
│    ├─ DS18B20.read()        → 24.5°C                       │
│    └─ RCWL×4.read()         → [45, 44, 46, 43] cm          │
│         │                                                    │
│         └─ calculate_canopy()                               │
│            └─ altura: 155.3cm, uniformidad: 2.8cm           │
└─────────────────────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. PUBLICACIÓN MQTT                                         │
│                                                              │
│    Topic: verdant/zone1/sensors                            │
│    Payload: {                                               │
│      "timestamp": 1708108800,                               │
│      "temperatura": 24.5,                                   │
│      "luz_lux": 18000,                                      │
│      "canopy": {                                            │
│        "altura_cm": 155.3,                                  │
│        "uniformidad_cm": 2.8,                               │
│        "distancias": {                                      │
│          "norte": 45, "sur": 44,                           │
│          "este": 46, "oeste": 43                           │
│        }                                                    │
│      }                                                      │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. ALMACENAMIENTO LOCAL (Pi 4B)                             │
│                                                              │
│    FastAPI suscribe MQTT                                   │
│    ├─ Recibe payload                                        │
│    ├─ Inserta en SQLite                                     │
│    │  └─ lecturas_sensores (synced=False)                  │
│    └─ Si cada 6h                                            │
│       └─ Calcula mapa_densidad                              │
│          └─ Inserta en mapas_densidad                       │
└─────────────────────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. SYNC A FIREBASE (cada 5 min)                             │
│                                                              │
│    Sync Service                                             │
│    ├─ SELECT * FROM lecturas_sensores WHERE synced=0       │
│    ├─ Batch upload a Firestore                              │
│    │  └─ /zones/zone1/readings/{timestamp}                 │
│    └─ UPDATE lecturas_sensores SET synced=1                │
└─────────────────────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. VISUALIZACIÓN                                            │
│                                                              │
│    PWA (React)                                              │
│    ├─ onSnapshot('/zones/zone1/readings')                  │
│    ├─ Actualiza gráficos en tiempo real                    │
│    └─ Muestra mapa 3D del canopy                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Flujo de Datos — Comando de Usuario

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USUARIO PRESIONA BOTÓN (celular 4G)                      │
│                                                              │
│    PWA en celular                                           │
│    └─ Click "Apagar extractor"                              │
└─────────────────────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ESCRITURA EN FIRESTORE (~200ms)                          │
│                                                              │
│    Firebase.firestore()                                     │
│      .collection('commands')                                │
│      .add({                                                 │
│        zone: 'zone1',                                       │
│        relay: 'extractor',                                  │
│        state: false,                                        │
│        timestamp: now(),                                    │
│        user: 'cuidador_maria'                               │
│      })                                                     │
└─────────────────────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. LISTENER DETECTA CAMBIO (~300ms)                         │
│                                                              │
│    Pi 4B - Firebase Listener                               │
│    └─ db.collection('commands')                             │
│       .onSnapshot(snapshot => {                             │
│         for (change in snapshot.changes) {                  │
│           if (change.type === 'ADDED') {                   │
│             cmd = change.data()                             │
│             publish_mqtt(cmd)                               │
│           }                                                 │
│         }                                                   │
│       })                                                    │
└─────────────────────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. PUBLICACIÓN MQTT LOCAL (~100ms)                          │
│                                                              │
│    Mosquitto                                                │
│    └─ Topic: verdant/zone1/cmd/relay                        │
│       Payload: {                                            │
│         "relay": "extractor",                               │
│         "state": false                                      │
│       }                                                     │
└─────────────────────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. PICO W EJECUTA (~200ms)                                  │
│                                                              │
│    Pico W #1 - MQTT subscriber                             │
│    ├─ Recibe comando                                        │
│    ├─ relay.set_extractor(False)                           │
│    └─ Publica confirmación                                  │
│       └─ verdant/zone1/status {"extractor": false}         │
└─────────────────────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. FEEDBACK AL USUARIO (~100ms)                             │
│                                                              │
│    PWA actualiza UI                                         │
│    └─ Botón cambia a estado "OFF"                           │
│       └─ Latencia total: ~1 segundo ✅                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Modos de Operación

### Modo Normal (todo funcionando)

```
Internet:  ✅
Pi 4B:     ✅ Online
Pico W:    ✅ Connected
Firebase:  ✅ Syncing

Flujo:
├─ Sensores → MQTT → Pi → SQLite
├─ Pi → Firebase (cada 5min)
├─ Usuario remoto → Firebase → Pi → MQTT → Pico W
└─ Tablet local → FastAPI → SQLite directo
```

### Sin Internet (Pi online, Firebase offline)

```
Internet:  ❌
Pi 4B:     ✅ Online
Pico W:    ✅ Connected
Firebase:  ❌ No sync

Flujo:
├─ Sensores → MQTT → Pi → SQLite ✅
├─ Pi → Firebase (bufferea, reintenta)
├─ Usuario remoto → ❌ No puede acceder
└─ Tablet local → FastAPI → SQLite directo ✅

Datos se acumulan en SQLite (synced=0)
Al volver internet → sync automático
```

### Pi Caída (Pico W autónomo)

```
Internet:  ❓ (irrelevante)
Pi 4B:     ❌ Offline
Pico W:    ✅ Autónomo
Firebase:  ❌ No data

Flujo:
├─ Sensores → evaluación local en Pico W
├─ Failsafe básico activo (temp > 35°C → extractor)
├─ NO hay registro de datos
└─ Al volver Pi → resync, datos perdidos

Este es el backup de emergencia
Pico W guarda último config en flash
```

---

## Estructura de Archivos en el Proyecto

```
VerdantCanopy/
├── hub/
│   ├── app/
│   │   ├── main.py              # FastAPI app principal
│   │   ├── mqtt/
│   │   │   ├── __init__.py
│   │   │   ├── broker.py        # Cliente MQTT
│   │   │   └── handlers.py      # Handlers por topic
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── sensors.py       # Endpoints lecturas
│   │   │   ├── events.py        # Endpoints eventos usuario
│   │   │   ├── zones.py         # Endpoints zonas
│   │   │   └── relays.py        # Endpoints control relays
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── models.py        # SQLAlchemy models
│   │   │   ├── schema.sql       # Schema completo
│   │   │   └── queries.py       # Queries comunes
│   │   ├── firebase/
│   │   │   ├── __init__.py
│   │   │   ├── listener.py      # onSnapshot realtime
│   │   │   ├── sync.py          # Batch upload
│   │   │   └── admin.py         # Firebase Admin SDK
│   │   └── utils/
│   │       ├── spatial.py       # Cálculos geométricos
│   │       └── density.py       # Mapas de densidad
│   ├── requirements.txt
│   ├── config.py
│   └── tests/
│
├── firmware/
│   ├── picow/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── sensors.py
│   │   ├── mqtt_client.py
│   │   ├── relay.py
│   │   └── failsafe.py
│   ├── ARCHITECTURE.md
│   ├── PINOUT.md
│   └── WIRING.md
│
├── pwa/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ZoneView.jsx
│   │   │   ├── Canopy3D.jsx
│   │   │   ├── SensorChart.jsx
│   │   │   └── EventLog.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Zones.jsx
│   │   │   ├── History.jsx
│   │   │   └── Settings.jsx
│   │   ├── hooks/
│   │   │   ├── useFirestore.js
│   │   │   ├── useRealtimeData.js
│   │   │   └── useOffline.js
│   │   ├── services/
│   │   │   ├── firebase.js
│   │   │   ├── local-api.js    # FastAPI local
│   │   │   └── storage.js      # IndexedDB offline
│   │   ├── App.jsx
│   │   └── sw.js               # Service Worker
│   ├── public/
│   │   ├── manifest.json        # PWA manifest
│   │   └── icons/
│   ├── package.json
│   └── firebase.json
│
├── functions/
│   ├── index.js                 # Cloud Functions
│   ├── package.json
│   └── .firebaserc
│
├── docs/
│   ├── verdant-checkpoint.html
│   ├── verdant-architecture.html
│   ├── verdant-stack.html
│   ├── DATABASE_SCHEMA.md
│   └── SYSTEM_ARCHITECTURE.md   # este archivo
│
├── CHANGELOG.md
├── README.md
└── .gitignore
```

---

## Stack Tecnológico Completo

| Capa | Tecnología | Versión | Propósito |
|------|-----------|---------|-----------|
| **Edge** | MicroPython | 1.22+ | Firmware Pico W |
| | Machine | built-in | GPIO/I²C/ADC |
| **Hub** | Ubuntu Server | 24.04 LTS | OS Pi 4B |
| | Python | 3.12 | Runtime |
| | FastAPI | 0.109+ | HTTP API |
| | Uvicorn | 0.27+ | ASGI server |
| | SQLite | 3.45+ | Database local |
| | SQLAlchemy | 2.0+ | ORM |
| | Mosquitto | 2.0+ | MQTT broker |
| | paho-mqtt | 1.6+ | MQTT client |
| | firebase-admin | 6.4+ | Firebase SDK |
| | hostapd | 2.10+ | WiFi AP |
| | dnsmasq | 2.89+ | DHCP/DNS |
| **Cloud** | Firebase Firestore | - | NoSQL DB |
| | Firebase Auth | - | Authentication |
| | Cloud Functions | Node.js 20 | Serverless |
| | Firebase Hosting | - | PWA host |
| | FCM | - | Push web |
| **Frontend** | React | 18+ | UI framework |
| | Three.js | r160+ | 3D viz |
| | Recharts | 2.10+ | Charts |
| | Firebase SDK | 10.8+ | Web SDK |
| | Workbox | 7.0+ | Service Worker |

---

## Seguridad

```
┌────────────────────────────────────────────────────────┐
│ Red Local (WiFi Hotspot Pi 4B)                         │
│ ────────────────────────────────────────────────────   │
│ Sin autenticación — red privada                        │
│ FastAPI sin JWT — confianza en red local               │
│ MQTT sin auth — solo accesible localmente              │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ Firebase (acceso remoto)                               │
│ ────────────────────────────────────────────────────   │
│ Firebase Auth con Google                               │
│ Custom claims para RBAC                                │
│ Firestore Security Rules:                              │
│   - Leer: autenticado con claim.role                   │
│   - Escribir: solo admins                              │
│ HTTPS obligatorio                                      │
└────────────────────────────────────────────────────────┘
```

---

## Monitoreo y Logs

```
Pi 4B:
├── /var/log/verdant/
│   ├── fastapi.log          # HTTP requests
│   ├── mqtt.log             # MQTT traffic
│   ├── firebase-sync.log    # Sync status
│   └── system.log           # General errors

Firebase:
├── Cloud Functions logs     # Function execution
└── Firestore usage stats    # Reads/writes

PWA:
├── IndexedDB                # Offline data
└── Service Worker cache     # Cached assets
```

---

## Deployment

```bash
# Pi 4B setup
ssh pi@192.168.1.X
git clone https://github.com/user/verdant-canopy
cd verdant-canopy/hub
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl enable verdant-api verdant-sync
sudo systemctl start verdant-api verdant-sync

# Firebase setup
cd ../functions
npm install
firebase login
firebase deploy --only functions,hosting

# PWA build
cd ../pwa
npm install
npm run build
firebase deploy --only hosting

# Pico W flash
# Via Thonny: File → Open → firmware/picow/*.py
# Save each to Pico W
```

---

Este es el sistema completo.
