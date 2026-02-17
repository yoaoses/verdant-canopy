"""
Lectura de sensores - Pico W #1
Por ahora datos simulados, después hardware real
"""
import time
import random

class Sensors:
    def __init__(self):
        print("Sensors: inicializando (simulado)")
        # Cuando conectemos hardware:
        # self.i2c = I2C(0, scl=Pin(1), sda=Pin(0))
        # self.bh1750 = BH1750(self.i2c)
        # self.ds18b20 = DS18X20(OneWire(Pin(2)))
        # self.rcwl = [RCWL(pin) for pin in RCWL_PINS]
    
    def read_light(self):
        """Lee BH1750 - lux"""
        # Simulado: varía según hora del día
        hour = time.localtime()[3]
        if 6 <= hour <= 20:  # día
            return round(random.uniform(15000, 40000), 0)
        else:  # noche
            return 0.0
    
    def read_temperature(self):
        """Lee DS18B20 - temperatura ambiente °C"""
        # Simulado: rango realista 18-28°C
        return round(random.uniform(18.0, 28.0), 1)
    
    def read_canopy_map(self):
        """Lee 4 RCWL-1601 - distancias desde techo a canopy"""
        # Simulado: 4 distancias en cm
        # Techo está a 200cm, canopy entre 150-160cm
        return {
            "norte": round(random.uniform(40, 50), 1),  # distancia desde techo
            "sur": round(random.uniform(40, 50), 1),
            "este": round(random.uniform(40, 50), 1),
            "oeste": round(random.uniform(40, 50), 1),
        }
    
    def calculate_canopy_height(self, distances, techo_cm=200):
        """Calcula altura promedio del canopy"""
        avg_distance = sum(distances.values()) / len(distances)
        altura = techo_cm - avg_distance
        uniformidad = max(distances.values()) - min(distances.values())
        return {
            "altura_cm": round(altura, 1),
            "uniformidad_cm": round(uniformidad, 1)
        }
