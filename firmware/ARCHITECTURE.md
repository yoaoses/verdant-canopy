# Verdant Canopy — Arquitectura de Comunicación

Sistema híbrido MQTT + HTTP para comandos urgentes y sincronización periódica.

---

## Topología de Red

```
┌─────────────────────────────────────────────────────────┐
│           Raspberry Pi 4B (Hub Central)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Mosquitto   │  │   FastAPI    │  │   SQLite     │  │
│  │  MQTT Broker │  │   HTTP API   │  │   Config DB  │  │
│  │  :1883       │  │   :8000      │  │              │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │          │
│         └─────────────────┴─────────────────┘          │
└─────────────────────────────────────────────────────────┘
         │                 │
         │ MQTT            │ HTTP
         │ (comandos)      │ (sync)
         ▼                 ▼
┌────────────────┐  ┌────────────────┐
│   Pico W #1    │  │   Pico W #2    │
│ Ambiente+Canopy│  │  Calidad Agua  │
└────────────────┘  └────────────────┘
         │
         │ MQTT (solo publicar)
         ▼
┌────────────────┐
│  ESP8266 (opt) │
│ Sensores extra │
└────────────────┘
```

---

## Dos Canales de Comunicación

### Canal 1: HTTP Sync (cada 5 minutos)
**Propósito:** Sincronización bidireccional de datos + configuración

```
┌──────────┐                              ┌─────────┐
│ Pico W   │   POST /api/sync             │  Pi 4B  │
│          ├─────────────────────────────►│         │
│          │   body: sensor readings      │         │
│          │                               │         │
│          │   200 OK                      │         │
│          │◄─────────────────────────────┤         │
│          │   body: config JSON           │         │
└──────────┘                              └─────────┘
```

**Request (Pico W → Pi):**
```json
POST /api/sync
{
  "node_id": "picow1",
  "timestamp": 1708108800,
  "sensors": {
    "temperatura": 24.5,
    "luz_lux": 18000,
    "canopy": {
      "altura_cm": 155.3,
      "uniformidad_cm": 4.2,
      "distancias": {
        "norte": 44.7,
        "sur": 45.5,
        "este": 44.8,
        "oeste": 45.0
      }
    }
  },
  "relays_state": {
    "luz": true,
    "extractor": false
  },
  "config_version": 41  // versión que tiene cacheada
}
```

**Response (Pi → Pico W):**
```json
200 OK
{
  "config_version": 42,  // nueva versión si cambió
  "timestamp": 1708108805,
  "umbrales": {
    "temp_max": 28.0,
    "temp_min": 16.0,
    "altura_max": 180.0
  },
  "luz_schedule": {
    "mode": "18/6",
    "on_time": "06:00",
    "off_time": "00:00"
  },
  "failsafe_rules": [
    {
      "condition": "temperatura > umbrales.temp_max",
      "action": "extractor_on",
      "priority": "high"
    },
    {
      "condition": "luz_lux < 1000 AND schedule_should_be_on",
      "action": "alert_luz_fallo",
      "priority": "medium"
    },
    {
      "condition": "altura > umbrales.altura_max",
      "action": "alert_altura",
      "priority": "medium"
    }
  ],
  "sync_interval": 300  // puede ajustarse dinámicamente
}
```

**Flujo de actualización:**
1. Usuario cambia umbral en dashboard: temp_max = 30°C
2. Dashboard → FastAPI → SQLite actualiza config
3. SQLite incrementa `config_version` → 43
4. Próximo sync (< 5 min) → Pico recibe nueva versión
5. Pico cachea en flash → persiste si se reinicia

---

### Canal 2: MQTT (tiempo real < 1s)
**Propósito:** Comandos urgentes del usuario + telemetría continua

#### Topics:

```
verdant/zone1/sensors        → Pico W publica cada 30s
verdant/zone1/canopy         → Pico W publica cada 6h
verdant/zone1/status         → Pico W publica estado actual
verdant/zone1/cmd/relay      → Pi publica comandos urgentes
verdant/zone1/cmd/config     → Pi publica cambios inmediatos
```

#### Comando urgente (usuario presiona botón):

```
Usuario toca "Apagar extractor" en tablet
        ↓
Tablet → FastAPI POST /relay/extractor/off
        ↓
FastAPI → MQTT publish verdant/zone1/cmd/relay
{
  "relay": "extractor",
  "state": false,
  "timestamp": 1708108900,
  "source": "user",
  "user_id": "cuidador_maria"
}
        ↓
Pico W (escucha permanente) → recibe en ~500ms
        ↓
Pico W → relay.set_extractor(False)
        ↓
Pico W → MQTT publish verdant/zone1/status
{
  "extractor": false,
  "changed_at": 1708108900,
  "ack": true
}
        ↓
Tablet actualiza UI → feedback visual inmediato
```

**Latencia total:** **< 1 segundo** desde tap hasta ejecución.

---

## Failsafe Local en Pico W

El Pico W ejecuta las reglas del JSON **localmente** cada vez que lee sensores:

```python
# Cada 30 segundos en el Pico W
sensors_data = sensors.read_all()
config = load_cached_config()  # del último sync

for rule in config['failsafe_rules']:
    if evaluate_condition(rule['condition'], sensors_data, config):
        execute_action(rule['action'])
        publish_alert(rule)
```

**Si la Pi cae:**
- Pico sigue ejecutando con el último config cacheado
- Failsafe funciona normalmente
- Al volver la Pi → sync recupera datos acumulados

---

## Almacenamiento en Pico W

```python
# En flash del Pico W (persiste reinicio)
config.json         → último config recibido de la Pi
sensor_buffer.json  → lecturas no enviadas (si Pi cae)
```

**Capacidad:** 2MB flash libre → ~500 lecturas buffereadas

---

## Ciclo de Luz Programado

El Pico W ejecuta el schedule **localmente sin consultar a la Pi**:

```python
from config_cache import luz_schedule
import time

def check_luz_schedule():
    now = time.localtime()
    current_time = f"{now[3]:02d}:{now[4]:02d}"
    
    if luz_schedule['mode'] == '18/6':
        on_time = luz_schedule['on_time']   # "06:00"
        off_time = luz_schedule['off_time'] # "00:00"
        
        if on_time <= current_time < off_time:
            relay.set_luz(True)
        else:
            relay.set_luz(False)
    
    # Failsafe: verifica que la luz física responda
    if relay_luz_should_be_on() and sensors.read_light() < 1000:
        publish_alert("luz_fallo_electrico")
```

**Ventajas:**
- No depende de conexión en tiempo real
- Schedule se ejecuta incluso si la Pi está offline
- Cambios de schedule se sincronizan en el próximo HTTP sync

---

## ESP8266 como Sensores Adicionales

Los ESP8266/NodeMCU son **nodos simples** — solo publican datos:

```
ESP8266 → MQTT publish verdant/exterior/temp
{
  "temperatura": 12.5,
  "timestamp": 1708108800
}
```

**Sin:**
- Failsafe local
- Control de relays
- HTTP sync
- Lógica compleja

**Uso:** Sensores baratos para zonas secundarias donde no necesitas control.

---

## Resiliencia y Recuperación

| Escenario | Comportamiento |
|-----------|----------------|
| Pi cae | Pico continúa con último config cacheado · bufferiza lecturas |
| WiFi cae | Pico funciona standalone · datos buffereados en flash |
| Pico reinicia | Lee config.json de flash · recupera estado en < 3s |
| MQTT cae | HTTP sync sigue funcionando (5 min) · comandos urgentes fallan |
| HTTP cae | MQTT sigue funcionando · config no actualiza |
| Todo cae | Pico ejecuta failsafe básico hardcoded (temp > 35°C → extractor) |

---

## Endpoints FastAPI en Pi 4B

```
POST   /api/sync                → sync bidireccional Pico W
POST   /api/relay/:name/:state  → comando relay urgente
GET    /api/sensors             → lee últimas lecturas
GET    /api/config              → config actual
PUT    /api/config              → actualiza config (dashboard)
POST   /api/alerts              → registra alerta
GET    /api/zones/:id/status   → estado zona completo
```

---

## Seguridad

- **Red local cerrada:** WiFi hotspot propio de la Pi
- **Sin SSL en MQTT local:** overhead innecesario en red privada
- **Auth en HTTP:** JWT en requests del dashboard web remoto
- **MQTT sin auth:** solo accesible desde red local

---

## Monitoreo y Debug

Cada mensaje MQTT incluye timestamp — permite reconstruir secuencia de eventos:

```
# En la Pi - log completo del sistema
tail -f /var/log/verdant/mqtt.log

2024-02-17 14:23:01 [RECV] verdant/zone1/sensors {"temp": 24.5, "luz": 18000}
2024-02-17 14:23:05 [SEND] verdant/zone1/cmd/relay {"extractor": true}
2024-02-17 14:23:06 [RECV] verdant/zone1/status {"extractor": true, "ack": true}
```

Útil para debugging y análisis post-mortem si algo falla.
