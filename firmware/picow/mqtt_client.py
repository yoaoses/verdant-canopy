"""
Cliente MQTT - Pico W #1
Por ahora comentado, se activa cuando tengamos WiFi + Pi
"""

class MQTTClient:
    def __init__(self):
        print("MQTT: no conectado (modo standalone)")
        self.connected = False
    
    def connect(self):
        """Conecta al broker MQTT de la Pi"""
        # TODO: implementar cuando tengamos WiFi
        pass
    
    def publish(self, topic, data):
        """Publica datos al broker"""
        # TODO: implementar
        print(f"MQTT (simulado): {topic} → {data}")
    
    def check_messages(self):
        """Revisa si hay comandos del broker"""
        # TODO: implementar
        pass
