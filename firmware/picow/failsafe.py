"""
Reglas failsafe - Pico W #1
Estas reglas corren localmente, sin red, sin Pi
"""
from config import TEMP_MAX, TEMP_MIN, ALTURA_ALERTA

class Failsafe:
    def __init__(self, relay_controller):
        self.relay = relay_controller
        self.alerts = []
    
    def check(self, sensor_data):
        """Evalúa todas las reglas y actúa si es necesario"""
        temp = sensor_data.get("temperatura", 20)
        altura = sensor_data.get("canopy_altura", 0)
        
        # Regla 1: Temperatura crítica alta
        if temp > TEMP_MAX:
            print(f"⚠️ FAILSAFE: temp {temp}°C > {TEMP_MAX}°C")
            self.relay.set_extractor(True)  # enciende extractor
            self.alerts.append({"tipo": "temp_alta", "valor": temp})
        
        # Regla 2: Temperatura crítica baja
        elif temp < TEMP_MIN:
            print(f"⚠️ FAILSAFE: temp {temp}°C < {TEMP_MIN}°C")
            # Aquí iría el calefactor si lo tuviéramos
            self.alerts.append({"tipo": "temp_baja", "valor": temp})
        
        # Regla 3: Canopy cerca del techo
        if altura > ALTURA_ALERTA:
            print(f"⚠️ FAILSAFE: canopy {altura}cm cerca del techo")
            self.alerts.append({"tipo": "altura_alerta", "valor": altura})
        
        return self.alerts
