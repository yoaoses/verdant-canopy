# Changelog — Decisiones de Diseño

## 2024-02-17 — PWA en vez de Android nativo

**Decisión:** Frontend único como Progressive Web App.

**Razón:**
- Firebase Web SDK más simple que Android nativo
- Un solo código React para tablet, celular, PC
- Service Workers → funciona offline
- Chrome kiosk mode en tablet = mismo resultado que app nativa

**Cambios técnicos:**
- `dashboard/` → `pwa/` (React PWA)
- Eliminado `android/` (Android Studio ya no necesario)
- Stack: React + Firebase Web SDK + Service Workers

**Impacto docs:**
- HTML docs mencionan "Android app" → leer como "PWA"
- Stack.html lista Android Studio → ignorar
- Actualización completa de docs → post Beta 1

**Modo kiosk:**
- Tablet: Chrome fullscreen + Kiosk Browser Lockdown app
- Gesto secreto para salir
- Pantalla siempre encendida

## 2024-02-17 — Firebase listener en tiempo real

**Decisión:** Pi escucha Firestore con onSnapshot para comandos remotos.

**Flujo:**
1. Usuario remoto (4G) → Firebase escribe comando
2. Pi listener detecta cambio (< 500ms)
3. Pi publica MQTT local → Pico W ejecuta

**Costo:** Gratis en plan Spark (< 500 comandos/día)

**Implementación:** `hub/firebase_listener.py`
EOF

# 4. Actualizar README.md
cat > README.md << 'EOF'
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
| Hub local | Raspberry Pi 4B · Ubuntu 24 | MQTT broker + FastAPI + Firebase listener |
| Nube | Firebase (Firestore · Auth · Functions · Hosting) | Acceso remoto + alertas + historial |
| Frontend | React PWA | Una sola app: tablet kiosk + celular + PC |

## Estructura del Proyecto
```
hub/              Python · FastAPI · MQTT · Firebase Admin SDK
firmware/         MicroPython · Pico W · ESP8266
pwa/              React · Firebase Web SDK · Service Workers
functions/        Node.js · Cloud Functions · Alertas
docs/             HTML · Arquitectura · Stack · Checkpoint
```

## Documentación

- [Checkpoint de diseño](docs/verdant-checkpoint.html)
- [Arquitectura del sistema](docs/verdant-architecture.html)
- [Stack tecnológico](docs/verdant-stack.html)
- [Changelog de decisiones](CHANGELOG.md) ← **cambios recientes**

## Modo Kiosk (Tablet)

La tablet corre la PWA en Chrome con **Kiosk Browser Lockdown**:
- Pantalla completa, sin barra de navegación
- Gesto secreto para salir
- Funciona offline con Service Workers
- Se actualiza automáticamente cuando hay internet

## Contexto Legal

Desarrollado inicialmente para cultivo de cannabis medicinal (aceite CBD)
bajo autocultivo legal autorizado en Chile (Decreto 298, Ministerio de Salud).
El sistema es agnóstico al cultivo — el usuario es responsable de cumplir
la normativa vigente en su país.

## Roadmap

- [x] Diseño de arquitectura y stack
- [x] Estructura del proyecto
- [x] Firmware Pico W base (simulado)
- [ ] Hub Pi 4B — Mosquitto + FastAPI
- [ ] Firebase listener en tiempo real
- [ ] PWA base con Firebase SDK
- [ ] Integración completa Pico W → Pi → Firebase → PWA

## Licencia

MIT · Open Source · Valdivia, Chile 🇨🇱
EOF
