# 🌿 Verdant Canopy

Smart monitoring for every grow.

Sistema open source de monitoreo y automatización para ambientes de cultivo
controlado — invernaderos, indoor, hongos, hortalizas, hierbas medicinales.

Diseñado para funcionar sin internet. Se sincroniza cuando hay conexión.
Resiste fallos en cualquier capa.

## Arquitectura

| Capa | Tecnología | Rol |
|------|-----------|-----|
| Nodos edge | Pico W · ESP8266 · MicroPython | Sensores + relay + failsafe autónomo |
| Hub local | Raspberry Pi 4B · Ubuntu 24 | MQTT broker + API local + sync |
| Nube | Firebase (Firestore · Auth · Functions · Hosting) | Acceso remoto + alertas + historial |
| Interfaces | Android (dual mode) · React · Tablet kiosk | Control y visualización |

## Documentación

- [Checkpoint de diseño](docs/verdant-checkpoint.html)
- [Arquitectura del sistema](docs/verdant-architecture.html)
- [Stack tecnológico](docs/verdant-stack.html)

## Contexto legal

Desarrollado inicialmente para cultivo de cannabis medicinal (aceite CBD)
bajo autocultivo legal autorizado en Chile (Decreto 298, Ministerio de Salud).
El sistema es agnóstico al cultivo — el usuario es responsable de cumplir
la normativa vigente en su país.

## Licencia

MIT · Open Source · Valdivia, Chile 🇨🇱
