# Verdant Canopy — Wiring Guide

Circuitos conceptuales y guía de cableado para todos los componentes del sistema.

---

## Convenciones

```
Símbolos usados en diagramas ASCII:
─── Conexión directa
┴┬┤├ Intersecciones
[R] Resistencia
GND Tierra/Ground
VCC Voltaje positivo (3.3V o 5V)
```

---

## Circuito 1: BH1750 (Sensor de Luz)

```
Pico W #1                    BH1750
─────────────────────────────────────
                          ┌──────────┐
    3V3 ─────────────────►│ VCC      │
                          │          │
    GP0 (SDA) ────────┬──►│ SDA      │
                      │   │          │
    GP1 (SCL) ────────┼──►│ SCL      │
                      │   │          │
    GND ───────────┬──┴──►│ GND      │
                   │      │          │
                   │      │ ADDR     │◄── GND (dirección 0x23)
                   │      └──────────┘    o VCC (dirección 0x5C)
                   │
                   │  Pull-up resistors (4.7kΩ)
                   │  ┌────[4.7k]────┐
                   │  │              │
    3V3 ───────────┴──┴──────────────┘
                      SDA          SCL
```

**Componentes necesarios:**
- 2× Resistencia 4.7kΩ (pull-up I²C)
- Cable: 4 líneas (VCC, GND, SDA, SCL)

**Distancia máxima:** 1 metro (I²C estándar)

---

## Circuito 2: DS18B20 (Sensor Temperatura)

```
Pico W #1                    DS18B20
─────────────────────────────────────
                          ┌──────────┐
    3V3 ─────────────────►│ VDD  (1) │
                          │          │
    GP2 ──────────────┬──►│ DQ   (2) │ Data (One-Wire)
                      │   │          │
    GND ──────────────┴──►│ GND  (3) │
                          └──────────┘
                      │
                      │  Pull-up 4.7kΩ
         3V3 ─────[4.7k]
                      │
                    Data
```

**Modo de operación:** Parásito o Externo

**Parásito mode (2 cables):**
- VDD conectado a GND
- Alimentación desde Data via pull-up
- Menos confiable, usar solo cables cortos (< 20cm)

**Externo mode (3 cables) — RECOMENDADO:**
- VDD conectado a 3.3V
- Pull-up obligatorio: 4.7kΩ entre Data y 3.3V
- Más confiable, soporta cables largos

**Multiples DS18B20 en un solo pin:**
```
Pico W GP2 ─────┬──[4.7k]── 3V3
                │
                ├─── DS18B20 #1 Data
                │
                ├─── DS18B20 #2 Data
                │
                └─── DS18B20 #3 Data

Cada sensor tiene ROM única (64-bit)
El código identifica cada uno por su ID
```

---

## Circuito 3: RCWL-1601 (Ultrasonido × 4)

```
Pico W #1                    RCWL-1601 Norte
─────────────────────────────────────────────
                          ┌──────────┐
    5V (VBUS) ───────────►│ VCC      │
                          │          │
    GP3 ──────────────┬──►│ Trig     │
                      └───┤ Echo     │ (modo combinado)
                          │          │
    GND ─────────────────►│ GND      │
                          └──────────┘

Repetir para:
- RCWL Sur  → GP4
- RCWL Este → GP5
- RCWL Oeste → GP6
```

**Distribución física — vista desde arriba:**

```
         ┌────────────────────┐
         │      Techo         │
         │                    │
   Norte │  [RCWL]            │
         │     ↓              │
         │                    │
  Oeste  │ [RCWL] → Planta ← [RCWL]  Este
         │                    │
         │     ↑              │
         │  [RCWL]            │
    Sur  │                    │
         └────────────────────┘

Los 4 sensores apuntan hacia abajo
al centro donde está el canopy
Distancia techo→sensor: 5-10cm
```

**Importante:**
- RCWL-1601 requiere 5V (NO funciona con 3.3V confiablemente)
- GPIO del Pico W es tolerante a 5V en modo INPUT
- Conectar VCC del sensor a VBUS (5V) del Pico W

---

## Circuito 4: Módulo Relay (2 canales)

```
Pico W #1              Relay Módulo             Carga AC
──────────────────────────────────────────────────────────
                    ┌─────────────────┐
  VBUS (5V) ───────►│ VCC             │
                    │                 │
  GP16 ────────────►│ IN1 (Luz)       │
                    │                 │
  GP17 ────────────►│ IN2 (Extractor) │
                    │                 │
  GND ─────────────►│ GND             │
                    │                 │
                    │  COM1 ────┐     │      ┌──── 220V L
                    │  NO1  ────┼─────┼──────┤
                    │           │     │      │  Ampolleta
                    │           └─────┼──────┤
                    │                 │      └──── 220V N
                    │  COM2 ────┐     │
                    │  NO2  ────┼─────┼───── Extractor
                    │           │     │
                    │           └─────┼───── (similar)
                    └─────────────────┘
```

**Lógica del relay:**
- Módulo con opto-acoplador: Activo en LOW
- Pico W envía `0` (LOW) → Relay cierra circuito (ON)
- Pico W envía `1` (HIGH) → Relay abre circuito (OFF)

**Seguridad eléctrica:**
```
CRÍTICO - 220V AC:
- Aislar completamente cables de alta tensión
- Usar caja de relays cerrada
- NO tocar terminales COM/NO con manos
- Probar primero con multímetro en continuidad
- Conectar carga AC DESPUÉS de verificar relay funciona con 5V DC
```

**Configuración inicial segura:**
```python
# En el firmware
relay_luz = Pin(16, Pin.OUT, value=1)      # HIGH = OFF al inicio
relay_extractor = Pin(17, Pin.OUT, value=1) # Fail-safe
```

---

## Circuito 5: PT100 con MAX31865 (Pico W #2)

```
Pico W #2                MAX31865              PT100
────────────────────────────────────────────────────
                      ┌─────────────┐
    3V3 ─────────────►│ VIN         │
                      │             │
    GP0 (SDA) ───────►│ SDA         │
                      │             │     ┌────────┐
    GP1 (SCL) ───────►│ SCL         │     │ PT100  │
                      │             │     │ RTD    │
    GND ─────────────►│ GND   RTD+  ├────►│ Red    │
                      │       RTD-  ├────►│ Red    │
                      │             │     └────────┘
                      └─────────────┘

Configurar MAX31865 para:
- 3-wire PT100 (común) o 2-wire
- Resistencia de referencia: 430Ω (verificar datasheet)
```

**Calibración:**
- Medir en hielo fundido (0°C) → ajustar offset
- Medir en agua hirviendo (100°C a nivel del mar) → ajustar ganancia

---

## Circuito 6: Sonda pH (Analógica)

```
Pico W #2                Módulo pH            Sonda pH
────────────────────────────────────────────────────────
                      ┌──────────────┐
    3V3 ─────────────►│ VCC          │     ┌─────────┐
                      │              │     │  Sonda  │
    GP26 (ADC0) ◄────┤ Analog OUT   │◄────┤  pH     │
                      │              │     │  (BNC)  │
    GND ─────────────►│ GND          │     └─────────┘
                      └──────────────┘

Salida: 0–3.3V proporcional a pH 0–14
Típico: pH 7 → 1.65V
```

**Calibración (esencial):**
1. Sumergir sonda en solución buffer pH 7.0
2. Ajustar potenciómetro del módulo hasta leer 1.65V
3. Repetir con buffer pH 4.0 y pH 10.0
4. Almacenar sonda en solución KCl 3M cuando no se usa

**Código de lectura:**
```python
from machine import ADC

ph_sensor = ADC(26)  # GP26
voltage = ph_sensor.read_u16() * 3.3 / 65535
ph_value = 7.0 + (1.65 - voltage) / 0.165  # calibración aproximada
```

---

## Circuito 7: TDS Metro (Analógico)

```
Pico W #2                TDS Módulo           Probe
────────────────────────────────────────────────────
                      ┌──────────────┐
    3V3 ─────────────►│ VCC    (R)   │     ┌──────┐
                      │              │     │ TDS  │
    GP27 (ADC1) ◄────┤ OUT    (Y)   │◄────┤ Probe│
                      │              │     │      │
    GND ─────────────►│ GND    (B)   │     └──────┘
                      └──────────────┘

Salida: 0–3.3V proporcional a conductividad
TDS (ppm) = voltage × factor_calibración
```

**Calibración:**
1. Sumergir probe en solución estándar 1413 µS/cm
2. Leer voltaje
3. `factor = 1413 / voltage_measured`
4. Enjuagar con agua destilada después de cada uso

---

## Circuito 8: Display OLED (Opcional Pico W #2)

```
Pico W #2                OLED 128x32
─────────────────────────────────────
                      ┌──────────┐
    3V3 ─────────────►│ VCC      │
                      │          │
    GP16 (SDA) ──────►│ SDA      │
                      │          │
    GP17 (SCL) ──────►│ SCL      │
                      │          │
    GND ─────────────►│ GND      │
                      └──────────┘

Dirección I²C: 0x3C (verificar con scan)
```

**Librería:** `ssd1306` para MicroPython

**Ejemplo de pantalla:**
```
┌────────────────┐
│ Agua de Riego  │
│ pH:  6.8  ✓    │
│ TDS: 820 ppm   │
│ [OK para regar]│
└────────────────┘
```

---

## Layout Físico Recomendado

### Disposición de Componentes

```
┌───────────────────────────────────────────────┐
│         Espacio de Cultivo (invernadero)      │
│                                               │
│  Techo ────────────────────────────────────   │
│    ↑ ↑ ↑ ↑                                    │
│    │ │ │ │  RCWL-1601 (×4) apuntando abajo   │
│    │ │ │ │                                    │
│    └─┴─┴─┘                                    │
│      🌿🌿🌿  ← Planta                          │
│     🌿🌿🌿🌿                                    │
│    🌿🌿🌿🌿🌿                                   │
│                                               │
│  [BH1750]  ← Sensor luz (altura planta)      │
│  [DS18B20] ← Sensor temp ambiente             │
│                                               │
│  ┌──────────────┐                            │
│  │  Pico W #1   │ ← En caja impermeable      │
│  │  + Relay     │                            │
│  └──────────────┘                            │
│                                               │
│  🚰 Depósito agua ──────────────────          │
│     │                                         │
│     ├─ [PT100] temp agua                     │
│     ├─ [pH] calidad                          │
│     └─ [TDS] sales                           │
│                                               │
│  ┌──────────────┐                            │
│  │  Pico W #2   │ ← Portátil, cerca depósito│
│  │  + Display   │                            │
│  └──────────────┘                            │
└───────────────────────────────────────────────┘

Fuera del invernadero:
┌──────────────┐
│ Raspberry    │
│ Pi 4B        │ ← En la casa, al lado del router
│ (Hub WiFi)   │
└──────────────┘
```

### Cableado Largo (> 50cm)

Para cables largos entre Pico W y sensores:

```
Cable apantallado recomendado para:
- I²C (BH1750, PT100): Cable cat5/cat6 → usa pares trenzados
- One-Wire (DS18B20): Cable apantallado, pantalla a GND
- Analógico (pH, TDS): Cable coaxial

Evitar ruido eléctrico:
- Separar cables de sensores de cables de 220V AC
- Cruzar cables AC y sensores en ángulo recto (no paralelos)
```

---

## Fuente de Poder — Distribución

```
┌──────────────────────────────────┐
│  Fuente 220V AC → 5V 3A          │
│  (ej: Mean Well RS-15-5)         │
└─────┬────────────────────────────┘
      │
      │ 5V @ 3A
      │
      ├─────┬──────────────────────► Pico W #1 VBUS
      │     │
      │     └──────────────────────► Módulo Relay VCC
      │
      └────────────────────────────► Pico W #2 VBUS

Protección:
- Fusible 5A en línea de 220V AC
- Varistor 275V en entrada AC (protección picos)
```

---

## Checklist de Ensamblaje

**Paso 1: Verificación Eléctrica**
- [ ] Medir voltaje fuente: 5V ±0.25V
- [ ] Verificar polaridad con multímetro
- [ ] GND común conectado entre todos los componentes

**Paso 2: Sensores I²C**
- [ ] Pull-ups 4.7kΩ instalados (SDA, SCL → 3.3V)
- [ ] Scan I²C detecta dispositivos (código test)
- [ ] Sin conflicto de direcciones

**Paso 3: Sensores One-Wire**
- [ ] Pull-up 4.7kΩ instalado (Data → 3.3V)
- [ ] DS18B20 detectado (lee ROM ID)
- [ ] Temperatura razonable (no 85°C falso)

**Paso 4: Sensores Analógicos**
- [ ] Voltaje de salida dentro de rango 0–3.3V
- [ ] Sonda pH calibrada con buffers
- [ ] TDS calibrado con solución estándar

**Paso 5: Relays**
- [ ] Relay activa con LOW (lógica correcta)
- [ ] Probado con carga pequeña (12V DC) primero
- [ ] Aislar correctamente 220V AC

**Paso 6: Sistema Completo**
- [ ] Firmware cargado en ambos Pico W
- [ ] LED parpadea correctamente al inicio
- [ ] Datos aparecen en consola serial
- [ ] MQTT conecta a la Pi (cuando esté lista)

---

## Troubleshooting Hardware

| Síntoma | Causa Probable | Diagnóstico | Solución |
|---------|---------------|-------------|----------|
| I²C no responde | Falta pull-up | Medir resistencia SDA/SCL → 3.3V | Agregar 4.7kΩ |
| DS18B20 = 85°C | Desconectado | Verificar continuidad cables | Revisar conexiones |
| DS18B20 = -127°C | Pull-up faltante | Medir voltaje Data pin | Agregar 4.7kΩ |
| pH inestable | Sonda seca | Inspección visual | Guardar en KCl 3M |
| TDS siempre 0 | Probe desconectado | Verificar continuidad | Revisar BNC |
| Relay no activa | Voltaje insuficiente | Medir VCC relay con multímetro | Conectar a 5V VBUS |
| RCWL lee 0 | Polaridad invertida | Verificar VCC/GND | Corregir conexión |
| Pico W se reinicia | Corto en 3.3V | Desconectar sensores uno por uno | Encontrar corto |
| ADC ruidoso | Cable largo sin apantallar | Medir con osciloscopio | Cable apantallado |

---

## Referencias para Fritzing

Para crear diagramas visuales en Fritzing:

**Componentes a buscar:**
- Raspberry Pi Pico W (community part)
- BH1750 (I²C light sensor)
- DS18B20 (waterproof temperature)
- HC-SR04 (similar al RCWL-1601 para referencia)
- 2-channel 5V relay module
- MAX31865 RTD amplifier
- Generic ADC sensor (pH, TDS)
- SSD1306 OLED 128x32

**Views a crear:**
1. Breadboard view (conceptual, para aprendizaje)
2. Schematic view (circuito eléctrico formal)
3. PCB view (si eventualmente hacemos PCB custom)

---

**Próximos pasos:**
1. Ensamblar Pico W #1 en breadboard con 1 sensor de prueba
2. Cargar firmware y verificar lectura
3. Agregar sensores uno por uno
4. Probar relay con carga de 12V DC primero
5. Integrar 220V AC solo cuando todo funcione perfecto

**Seguridad primero — no apurar la conexión de 220V.**
