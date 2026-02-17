"""
Configuración del Pico W #1 - Ambiente + Canopy
"""

# WiFi (comentado por ahora - primero probamos sin red)
# WIFI_SSID = "verdant-hub"
# WIFI_PASSWORD = "tu-password"

# MQTT Broker (comentado por ahora)
# MQTT_BROKER = "192.168.4.1"  # IP de la Pi 4B
# MQTT_PORT = 1883
# MQTT_TOPIC_BASE = "verdant/zone1"

# Pines GPIO
PIN_LED = "LED"
PIN_RELAY_LUZ = 16
PIN_RELAY_EXTRACTOR = 17

# I²C para BH1750 (cuando lo conectemos)
I2C_SCL = 1
I2C_SDA = 0

# One-wire para DS18B20 (cuando lo conectemos)
ONEWIRE_PIN = 2

# RCWL-1601 ultrasonido (cuando los conectemos)
RCWL_PINS = [3, 4, 5, 6]  # Norte, Sur, Este, Oeste

# Umbrales failsafe
TEMP_MAX = 32.0  # °C
TEMP_MIN = 14.0  # °C
ALTURA_TECHO = 200  # cm
ALTURA_ALERTA = 180  # cm

# Intervalos
SENSOR_INTERVAL = 30  # segundos - lectura ambiente
CANOPY_INTERVAL = 21600  # segundos - 6 horas para mapa canopy
