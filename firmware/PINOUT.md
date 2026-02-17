# Verdant Canopy — Pinout Completo

Asignación de pines GPIO para cada Pico W y sus sensores.

---

## Raspberry Pi Pico W — Pinout Reference

```
                    ┌─────────────┐
                    │    USB-C    │
                    └─────────────┘
                         ╔═══╗
        GP0 ────────────║ 1  40 ║──────────── VBUS (5V)
        GP1 ────────────║ 2  39 ║──────────── VSYS
        GND ────────────║ 3  38 ║──────────── GND
        GP2 ────────────║ 4  37 ║──────────── 3V3_EN
        GP3 ────────────║ 5  36 ║──────────── 3V3(OUT)
        GP4 ────────────║ 6  35 ║──────────── ADC_VREF
        GP5 ────────────║ 7  34 ║──────────── GP28 (ADC2)
        GND ────────────║ 8  33 ║──────────── GND
        GP6 ────────────║ 9  32 ║──────────── GP27 (ADC1)
        GP7 ────────────║10  31 ║──────────── GP26 (ADC0)
        GP8 ────────────║11  30 ║──────────── RUN
        GP9 ────────────║12  29 ║──────────── GP22
        GND ────────────║13  28 ║──────────── GND
       GP10 ────────────║14  27 ║──────────── GP21
       GP11 ────────────║15  26 ║──────────── GP20
       GP12 ────────────║16  25 ║──────────── GP19
       GP13 ────────────║17  24 ║──────────── GP18
        GND ────────────║18  23 ║──────────── GND
       GP14 ────────────║19  22 ║──────────── GP17
       GP15 ────────────║20  21 ║──────────── GP16
                         ╚═══╝
```

---

## Pico W #1 — Ambiente + Canopy

### Asignación de Pines

| Pin GPIO | Función | Protocolo | Sensor/Actuador | Notas |
|----------|---------|-----------|-----------------|-------|
| **GP0** | I²C0 SDA | I²C | BH1750 (luz) | Pull-up 4.7kΩ a 3.3V |
| **GP1** | I²C0 SCL | I²C | BH1750 (luz) | Pull-up 4.7kΩ a 3.3V |
| **GP2** | One-Wire Data | 1-Wire | DS18B20 (temp) | Pull-up 4.7kΩ a 3.3V |
| **GP3** | Trigger/Echo | Digital | RCWL-1601 Norte | Ultrasonido canopy |
| **GP4** | Trigger/Echo | Digital | RCWL-1601 Sur | Ultrasonido canopy |
| **GP5** | Trigger/Echo | Digital | RCWL-1601 Este | Ultrasonido canopy |
| **GP6** | Trigger/Echo | Digital | RCWL-1601 Oeste | Ultrasonido canopy |
| **GP16** | Relay OUT | Digital OUT | Relay Luz | Activo LOW |
| **GP17** | Relay OUT | Digital OUT | Relay Extractor | Activo LOW |
| **3V3** | Power OUT | — | VCC sensores | Max 300mA total |
| **GND** | Ground | — | GND sensores | Común a todos |
| **VBUS** | Power IN (5V) | — | Fuente 5V externa | Para relays |

### Diagrama de Conexión Conceptual

```
┌────────────────────────────────────────────────────────┐
│                    Pico W #1                           │
│                                                        │
│  GP0 (SDA) ────┬─── BH1750 SDA                        │
│  GP1 (SCL) ────┼─── BH1750 SCL                        │
│                │                                       │
│  GP2 ──────────┴─── DS18B20 Data (con pull-up 4.7k)  │
│                                                        │
│  GP3 ────────────── RCWL-1601 Norte (Trig+Echo)      │
│  GP4 ────────────── RCWL-1601 Sur                     │
│  GP5 ────────────── RCWL-1601 Este                    │
│  GP6 ────────────── RCWL-1601 Oeste                   │
│                                                        │
│  GP16 ───────────── Relay Módulo IN1 (Luz)           │
│  GP17 ───────────── Relay Módulo IN2 (Extractor)     │
│                                                        │
│  3V3 ────────────── VCC sensores (300mA max)         │
│  GND ────────────── GND común                         │
│  VBUS ───────────── 5V para relays                    │
└────────────────────────────────────────────────────────┘
```

### Notas Técnicas

**BH1750 (Luz):**
- Dirección I²C: 0x23 (ADDR pin a GND) o 0x5C (ADDR a VCC)
- Rango: 0–65535 lux
- Consumo: 0.12 mA activo

**DS18B20 (Temperatura):**
- Resistencia pull-up: 4.7kΩ entre Data y 3.3V
- Precisión: ±0.5°C
- Varios sensores pueden compartir el mismo pin (direccionamiento por ROM)

**RCWL-1601 (Ultrasonido):**
- Cada sensor usa 1 pin GPIO (modo Trigger=Echo combinado)
- Rango: 2cm – 400cm
- Ángulo: ~15°
- Consumo: 15mA c/u → 60mA total

**Relays:**
- Módulo activo en LOW (común en opto-acoplados)
- Pico W envía 0V (LOW) para activar relay
- Alimentación relay: VBUS 5V (NO de 3.3V — insuficiente)
- Máximo por relay: 10A @ 220V AC

---

## Pico W #2 — Calidad Agua de Riego

### Asignación de Pines

| Pin GPIO | Función | Protocolo | Sensor/Actuador | Notas |
|----------|---------|-----------|-----------------|-------|
| **GP0** | I²C0 SDA | I²C | PT100 intérprete | MAX31865 o similar |
| **GP1** | I²C0 SCL | I²C | PT100 intérprete | Pull-up 4.7kΩ |
| **GP26 (ADC0)** | Analog IN | ADC | Sonda pH | 0–3.3V |
| **GP27 (ADC1)** | Analog IN | ADC | TDS Metro | 0–3.3V |
| **GP16** | Display SDA | I²C | OLED 128x32 | Opcional para mostrar valores |
| **GP17** | Display SCL | I²C | OLED 128x32 | Dirección 0x3C |
| **3V3** | Power OUT | — | VCC sensores | Max 300mA |
| **GND** | Ground | — | GND común | — |

### Diagrama de Conexión Conceptual

```
┌────────────────────────────────────────────────────────┐
│                    Pico W #2                           │
│                                                        │
│  GP0 (SDA) ────┬─── MAX31865 (PT100) SDA             │
│  GP1 (SCL) ────┴─── MAX31865 SCL                     │
│                                                        │
│  GP26 (ADC0) ────── Sonda pH Analog OUT              │
│  GP27 (ADC1) ────── TDS Metro Analog OUT             │
│                                                        │
│  GP16 (SDA) ───┬─── OLED Display SDA (opcional)      │
│  GP17 (SCL) ───┴─── OLED Display SCL                 │
│                                                        │
│  3V3 ──────────────── VCC sensores                    │
│  GND ──────────────── GND común                       │
└────────────────────────────────────────────────────────┘
```

### Notas Técnicas

**PT100 con MAX31865:**
- PT100 es RTD (Resistance Temperature Detector)
- MAX31865 convierte resistencia → temperatura digital vía I²C/SPI
- Precisión: ±0.1°C
- Rango: -200°C a +850°C (usamos 0–40°C)

**Sonda pH:**
- Salida analógica: 0–3.3V proporcional a pH 0–14
- Requiere calibración con soluciones buffer (pH 4.0, 7.0, 10.0)
- Almacenar en solución KCl cuando no se usa

**TDS Metro:**
- Salida analógica proporcional a conductividad (ppm)
- Calibración con solución 1413 µS/cm
- Rango típico agua riego: 200–1500 ppm

**Display OLED (opcional):**
- 128x32 píxeles monocromo
- Muestra pH y TDS en tiempo real
- Usuario ve valores sin conectarse al WiFi
- Útil en el invernadero

---

## Alimentación

### Fuente de Poder 220V AC → Multi-salida

```
Entrada: 220V AC
Salidas:
├── 5V 3A   → VBUS ambos Pico W + relays
├── 3.3V 1A → (no usar, Pico W genera su propio 3.3V)
└── 12V 1A  → (reservado para ventiladores DC si se agregan)

Distribución:
┌────────────┐
│  Fuente    │
│  220V→5V   │
└─────┬──────┘
      │
      ├───► Pico W #1 VBUS (+ relays)
      ├───► Pico W #2 VBUS
      └───► Módulo relay VCC
```

**Importante:**
- NO alimentar relays desde 3.3V del Pico W — insuficiente corriente
- Usar VBUS (5V) para VCC del módulo relay
- Pico W regula internamente 3.3V para sus sensores

---

## Capacidad de Corriente

| Componente | Consumo | Cantidad | Total |
|------------|---------|----------|-------|
| Pico W | 50 mA | 2 | 100 mA |
| BH1750 | 0.12 mA | 1 | 0.12 mA |
| DS18B20 | 1 mA | 1 | 1 mA |
| RCWL-1601 | 15 mA | 4 | 60 mA |
| PT100 MAX31865 | 2 mA | 1 | 2 mA |
| Sonda pH | 5 mA | 1 | 5 mA |
| TDS Metro | 5 mA | 1 | 5 mA |
| OLED display | 20 mA | 1 | 20 mA |
| Relay módulo (standby) | 15 mA | 1 | 15 mA |
| **Total sensores** | | | **~208 mA** |

**Fuente 5V 3A** es más que suficiente (1500 mA disponibles).

---

## ESP8266 como Nodo Adicional (Opcional)

Si usas ESP8266 para sensores extra:

| Pin | Función | Sensor |
|-----|---------|--------|
| GPIO4 (D2) | I²C SDA | DHT22 o sensor adicional |
| GPIO5 (D1) | I²C SCL | — |
| GPIO14 (D5) | One-Wire | DS18B20 exterior |
| 3V3 | Power | VCC sensor |
| GND | Ground | GND común |

**Firmware:** Solo MicroPython que lee y publica MQTT — sin failsafe ni control.

---

## Diagrama General Sistema Completo

```
        ┌───────────────────────────┐
        │   Raspberry Pi 4B         │
        │   (WiFi Hotspot)          │
        │   192.168.4.1             │
        └─────────┬─────────────────┘
                  │ WiFi
          ┌───────┴─────────┬─────────────┐
          │                 │             │
    ┌─────▼─────┐     ┌─────▼─────┐  ┌───▼────┐
    │ Pico W #1 │     │ Pico W #2 │  │ ESP8266│
    │ Ambiente  │     │ Agua      │  │ Extra  │
    │ + Canopy  │     │           │  │        │
    └─────┬─────┘     └─────┬─────┘  └───┬────┘
          │                 │            │
    ┌─────▼──────┐    ┌─────▼──────┐  ┌─▼────┐
    │ Sensores   │    │ Sensores   │  │Sensor│
    │ Ambiente   │    │ Agua       │  │Extra │
    │ + Relays   │    │ + Display  │  │      │
    └────────────┘    └────────────┘  └──────┘
```

---

## Checklist Pre-Conexión

Antes de conectar hardware, verificar:

- [ ] Fuente de 5V genera voltaje estable (medir con multímetro)
- [ ] GND común conectado entre todos los componentes
- [ ] Pull-ups instalados en I²C (4.7kΩ entre SDA/SCL y 3.3V)
- [ ] Pull-up instalado en DS18B20 (4.7kΩ entre Data y 3.3V)
- [ ] Relays alimentados desde VBUS 5V, NO desde 3.3V
- [ ] Sensores analógicos (pH, TDS) NO exceden 3.3V
- [ ] Pico W tiene MicroPython flasheado
- [ ] LED del Pico W parpadea con script de test

---

## Troubleshooting Común

| Problema | Causa Probable | Solución |
|----------|---------------|----------|
| I²C no responde | Falta pull-up | Agregar 4.7kΩ entre SDA/SCL y 3.3V |
| DS18B20 lee 85°C | Sensor desconectado | Verificar conexiones + pull-up |
| Relay no activa | Alimentación insuficiente | Conectar VCC relay a VBUS 5V |
| RCWL lee siempre 0 | Sensor invertido | Verificar polaridad VCC/GND |
| pH inestable | Sonda seca | Guardar en solución KCl |
| Pico W no enciende | Corto en 3.3V | Desconectar sensores y probar |

---

**Próximo paso:** WIRING.md con diagramas de circuitos completos.
