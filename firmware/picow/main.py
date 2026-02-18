"""
Verdant Canopy - Firmware Pico W #1 (Ambiente + Canopy)

Este firmware lee sensores, ejecuta failsafe local, y publica a MQTT.
Por ahora funciona standalone con datos simulados.
"""
import time
from machine import Pin
from sensors import Sensors
from failsafe import Failsafe
from relay import RelayController
from mqtt_client import MQTTClient
from config import SENSOR_INTERVAL, CANOPY_INTERVAL

# LED interno para feedback visual
led = Pin("LED", Pin.OUT)

def blink(times=1):
    """Parpadea LED - feedback visual"""
    for _ in range(times):
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.1)

def main():
    print("=" * 40)
    print("Verdant Canopy - Pico W #1")
    print("Ambiente + Canopy")
    print("=" * 40)
    
    # Inicializar componentes
    sensors = Sensors()
    relay = RelayController()
    failsafe = Failsafe(relay)
    mqtt = MQTTClient()
    
    # Contadores
    last_sensor_read = 0
    last_canopy_read = 0
    
    blink(3)  # 3 parpadeos = inicio OK
    
    print("Loop principal iniciado")
    
    try:
        while True:
            now = time.time()
            
            # Lectura de sensores ambiente cada 30s
            if now - last_sensor_read >= SENSOR_INTERVAL:
                blink(1)
                
                # Leer sensores
                luz = sensors.read_light()
                temp = sensors.read_temperature()
                dht = sensors.read_dht11()
                hum_sustrato = sensors.read_humedad_sustrato()
                ph = sensors.read_ph()
                
                data = {
                    "timestamp": now,
                    "luz_lux": luz,
                    "temperatura_ds18": temp,
                    "temperatura_dht": dht["temperatura"],
                    "humedad_aire": dht["humedad"],
                    "humedad_sustrato": hum_sustrato,
                    "ph_agua": ph
                }
                
                print(f"Sensores: {temp}°C · {dht['humedad']}%RH · {luz} lux · pH {ph} · Sustrato {hum_sustrato}%")
                
                # Evaluar failsafe
                failsafe.check(data)
                
                # Publicar a MQTT (si está conectado)
                mqtt.publish("verdant/zone1/sensors", data)
                
                last_sensor_read = now
            
            # Lectura de mapa canopy cada 6 horas
            if now - last_canopy_read >= CANOPY_INTERVAL:
                print("Leyendo mapa canopy...")
                distances = sensors.read_canopy_map()
                canopy_info = sensors.calculate_canopy_height(distances)
                
                print(f"Canopy: {canopy_info['altura_cm']}cm · uniformidad {canopy_info['uniformidad_cm']}cm")
                
                # Evaluar altura
                failsafe.check({"canopy_altura": canopy_info['altura_cm']})
                
                mqtt.publish("verdant/zone1/canopy", {**distances, **canopy_info})
                
                last_canopy_read = now
            
            time.sleep(1)  # Loop cada 1 segundo
    
    except KeyboardInterrupt:
        print("\nDeteniendo...")
        relay.all_off()
        blink(5)  # 5 parpadeos = shutdown
        print("Firmware detenido")

if __name__ == "__main__":
    main()
