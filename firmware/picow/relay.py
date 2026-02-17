"""
Control de relés - Pico W #1
"""
from machine import Pin
from config import PIN_RELAY_LUZ, PIN_RELAY_EXTRACTOR

class RelayController:
    def __init__(self):
        # Relés activos en LOW (común en módulos con opto-acoplador)
        self.relay_luz = Pin(PIN_RELAY_LUZ, Pin.OUT, value=1)  # OFF al inicio
        self.relay_extractor = Pin(PIN_RELAY_EXTRACTOR, Pin.OUT, value=1)
        print("Relays: inicializados")
    
    def set_luz(self, state):
        """Luz: True=ON, False=OFF"""
        self.relay_luz.value(0 if state else 1)
        print(f"Relay Luz: {'ON' if state else 'OFF'}")
    
    def set_extractor(self, state):
        """Extractor: True=ON, False=OFF"""
        self.relay_extractor.value(0 if state else 1)
        print(f"Relay Extractor: {'ON' if state else 'OFF'}")
    
    def all_off(self):
        """Apaga todos los relés"""
        self.set_luz(False)
        self.set_extractor(False)
        print("Todos los relays apagados")
