# Verdant Canopy — Firestore Structure

Estructura de colecciones y documentos en Firebase Firestore.

---

## Jerarquía de Colecciones

```
firestore/
├── spaces/                          (colección raíz)
│   └── {space_id}/                 (documento)
│       ├── zones/                   (subcolección)
│       │   └── {zone_id}/          (documento)
│       │       ├── readings/        (subcolección)
│       │       │   └── {timestamp}/ (documento)
│       │       ├── density_maps/    (subcolección)
│       │       │   └── {timestamp}/ (documento)
│       │       └── events/          (subcolección)
│       │           └── {event_id}/  (documento)
│       └── sensors/                 (subcolección)
│           └── {sensor_id}/        (documento)
│
├── profiles/                        (colección raíz)
│   └── {profile_id}/               (documento)
│
├── commands/                        (colección raíz)
│   └── {command_id}/               (documento)
│
└── users/                           (colección raíz)
    └── {uid}/                      (documento)
        └── notifications/           (subcolección)
            └── {notif_id}/         (documento)
```

---

## Colección: spaces

```javascript
// Documento: /spaces/{space_id}
{
  "id": "space_valdivia_1",
  "name": "Indoor Principal",
  "location": "Valdivia, Chile",
  "dimensions": {
    "width_cm": 100,
    "length_cm": 100,
    "height_cm": 200
  },
  "owner_uid": "user_abc123",
  "created_at": Timestamp,
  "updated_at": Timestamp
}
```

---

## Subcolección: spaces/{id}/sensors

```javascript
// Documento: /spaces/space_valdivia_1/sensors/sensor_1
{
  "id": "sensor_1",
  "type": "rcwl",
  "name": "RCWL Norte",
  "position": {
    "x_cm": 50,
    "y_cm": 95,
    "z_cm": 195
  },
  "metadata": {
    "model": "RCWL-1601",
    "pin": 3
  },
  "status": "active"
}
```

---

## Subcolección: spaces/{id}/zones

```javascript
// Documento: /spaces/space_valdivia_1/zones/zone1
{
  "id": "zone1",
  "name": "Zona Cannabis Principal",
  "profile_id": "cannabis_indoor",
  "volume": {
    "x_min": 10,
    "y_min": 10,
    "z_min": 0,
    "x_max": 90,
    "y_max": 90,
    "z_max": 180,
    "total_cm3": 460800  // calculado
  },
  "status": "active",
  "start_date": "2024-02-01",
  "end_date": null,
  "current_phase": "crecimiento",
  "stats": {
    "days_active": 45,
    "last_reading": Timestamp,
    "current_occupancy_pct": 15.6
  }
}
```

---

## Subcolección: zones/{id}/readings

```javascript
// Documento: /spaces/.../zones/zone1/readings/1708108800000
{
  "timestamp": Timestamp(1708108800),
  "zone_id": "zone1",
  "node_id": "picow1",
  
  "sensors": {
    "temperatura": 24.5,
    "humedad": 62.0,
    "luz_lux": 18000,
    "co2_ppm": 820
  },
  
  "canopy": {
    "altura_cm": 155.3,
    "uniformidad_cm": 2.8,
    "distancias": {
      "norte": 45.2,
      "sur": 44.1,
      "este": 46.3,
      "oeste": 43.8
    }
  },
  
  "metadata": {
    "synced_from": "pi_hub",
    "firmware_version": "1.0.0"
  }
}
```

**Agregación:** Los readings se guardan cada 5 min (12 por hora).

```
Lecturas por día: 288
Lecturas por ciclo 90 días: 25,920
Tamaño aprox por lectura: 500 bytes
Total por ciclo: ~13 MB
```

**Estrategia de particionado:**
- Después de 30 días → mover a colección archive
- Mantener solo últimos 30 días en /readings activo

---

## Subcolección: zones/{id}/density_maps

```javascript
// Documento: /spaces/.../zones/zone1/density_maps/1708108800000
{
  "timestamp": Timestamp,
  "zone_id": "zone1",
  
  "metrics": {
    "volume_occupied_cm3": 72000,      // 72 litros
    "occupancy_pct": 15.6,
    "height_max_cm": 157.2,
    "height_avg_cm": 155.3,
    "height_min_cm": 152.8,
    "uniformity_cm": 4.4
  },
  
  "center_of_mass": {
    "x_cm": 50.2,
    "y_cm": 49.8,
    "z_cm": 155.3
  },
  
  "grid": {
    "resolution_cm": 10,
    "data": null  // Grid 3D opcional - pesado, solo si se pide
  }
}
```

**Agregación:** Se guardan cada 6 horas (4 por día).

```
Mapas por día: 4
Mapas por ciclo 90 días: 360
Tamaño aprox: 1 KB cada uno
Total: ~360 KB
```

---

## Subcolección: zones/{id}/events

```javascript
// Documento: /spaces/.../zones/zone1/events/event_abc123
{
  "id": "event_abc123",
  "timestamp": Timestamp,
  "zone_id": "zone1",
  
  "type": "riego",
  
  "position": {  // opcional
    "x_cm": 30,
    "y_cm": 40
  },
  
  "description": "Riego con pH 6.5, 500ml por maceta",
  
  "payload": {
    "ph": 6.5,
    "volume_ml": 1500,
    "water_type": "filtrada",
    "fertilizer": "flora_micro",
    "fertilizer_dose_ml": 5
  },
  
  "photos": [
    "https://storage.googleapis.com/.../photo1.jpg"
  ],
  
  "user": {
    "uid": "user_abc123",
    "display_name": "María",
    "role": "cuidador"
  },
  
  "synced_from": "firebase"  // o "pi_hub"
}
```

**Tipos de eventos:**
```
"siembra", "trasplante", "poda", "riego", 
"fertilizacion", "observacion", "ajuste_luz",
"ajuste_ventilacion", "cosecha_parcial", "otro"
```

---

## Colección: profiles

```javascript
// Documento: /profiles/cannabis_indoor
{
  "id": "cannabis_indoor",
  "name": "Cannabis Indoor Medicinal",
  "type_organism": "planta",
  
  "metrics": {
    "environment": [
      "temperatura", "humedad", "luz_dli", "co2"
    ],
    "water": [
      "ph", "tds", "volume_ml"
    ]
  },
  
  "thresholds": {
    "temp_min": 18,
    "temp_max": 28,
    "humidity_min": 40,
    "humidity_max": 70,
    "ph_min": 6.0,
    "ph_max": 7.0,
    "dli_min": 20,
    "dli_max": 45
  },
  
  "phases": [
    {
      "name": "germinacion",
      "duration_days": 7,
      "thresholds": {
        "temp_min": 22,
        "temp_max": 26,
        "humidity_min": 70,
        "humidity_max": 80
      }
    },
    {
      "name": "crecimiento",
      "duration_days": 30,
      "light_schedule": "18/6",
      "thresholds": {
        "temp_min": 20,
        "temp_max": 28,
        "humidity_min": 50,
        "humidity_max": 70
      }
    },
    {
      "name": "floracion",
      "duration_days": 60,
      "light_schedule": "12/12",
      "thresholds": {
        "temp_min": 18,
        "temp_max": 26,
        "humidity_min": 40,
        "humidity_max": 55
      }
    }
  ],
  
  "costs_reference": {
    "power_consumption_w_veg": 250,
    "power_consumption_w_flower": 250,
    "cost_kwh_clp": 150
  },
  
  "created_at": Timestamp,
  "is_default": true
}
```

---

## Colección: commands (temporal)

```javascript
// Documento: /commands/cmd_xyz789
{
  "id": "cmd_xyz789",
  "timestamp": Timestamp,
  
  "zone": "zone1",
  "type": "relay",
  
  "payload": {
    "relay": "extractor",
    "state": false
  },
  
  "user": {
    "uid": "user_abc123",
    "display_name": "María"
  },
  
  "status": "pending",  // "pending", "executed", "failed"
  "executed_at": null,
  
  "ttl": Timestamp + 5min  // auto-delete después de 5 min
}
```

**Lifecycle:**
```
1. Usuario crea comando → status: "pending"
2. Pi listener detecta → ejecuta
3. Pico W confirma → status: "executed"
4. TTL expira → auto-delete por Cloud Function
```

---

## Colección: users

```javascript
// Documento: /users/user_abc123
{
  "uid": "user_abc123",
  "email": "maria@example.com",
  "display_name": "María",
  "photo_url": "https://...",
  
  "role": "cuidador",  // "admin", "cuidador", "observador"
  
  "spaces_access": [
    {
      "space_id": "space_valdivia_1",
      "role": "cuidador",
      "granted_at": Timestamp
    }
  ],
  
  "preferences": {
    "language": "es",
    "timezone": "America/Santiago",
    "notifications": {
      "email": true,
      "push": true,
      "critical_only": false
    }
  },
  
  "last_active": Timestamp,
  "created_at": Timestamp
}
```

---

## Subcolección: users/{uid}/notifications

```javascript
// Documento: /users/user_abc123/notifications/notif_1
{
  "id": "notif_1",
  "timestamp": Timestamp,
  
  "type": "alert",  // "alert", "info", "success"
  "severity": "high",  // "low", "medium", "high", "critical"
  
  "title": "Temperatura Alta",
  "message": "Zona 1: 31°C detectado. Extractor activado automáticamente.",
  
  "zone_id": "zone1",
  "space_id": "space_valdivia_1",
  
  "read": false,
  "read_at": null,
  
  "action_url": "/zones/zone1"  // deeplink en PWA
}
```

---

## Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Helper functions
    function isAuthenticated() {
      return request.auth != null;
    }
    
    function hasRole(role) {
      return isAuthenticated() && 
             get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == role;
    }
    
    function hasAccessToSpace(spaceId) {
      return isAuthenticated() && 
             get(/databases/$(database)/documents/users/$(request.auth.uid))
               .data.spaces_access
               .hasAny([spaceId]);
    }
    
    // Spaces
    match /spaces/{spaceId} {
      allow read: if hasAccessToSpace(spaceId);
      allow write: if hasRole('admin');
      
      // Sensors
      match /sensors/{sensorId} {
        allow read: if hasAccessToSpace(spaceId);
        allow write: if hasRole('admin');
      }
      
      // Zones
      match /zones/{zoneId} {
        allow read: if hasAccessToSpace(spaceId);
        allow write: if hasRole('admin') || hasRole('cuidador');
        
        // Readings
        match /readings/{timestamp} {
          allow read: if hasAccessToSpace(spaceId);
          allow write: if false;  // Solo el backend escribe
        }
        
        // Density maps
        match /density_maps/{timestamp} {
          allow read: if hasAccessToSpace(spaceId);
          allow write: if false;
        }
        
        // Events
        match /events/{eventId} {
          allow read: if hasAccessToSpace(spaceId);
          allow create: if hasRole('admin') || hasRole('cuidador');
          allow update, delete: if hasRole('admin');
        }
      }
    }
    
    // Profiles (read-only para usuarios)
    match /profiles/{profileId} {
      allow read: if isAuthenticated();
      allow write: if hasRole('admin');
    }
    
    // Commands
    match /commands/{commandId} {
      allow read: if isAuthenticated();
      allow create: if hasRole('admin') || hasRole('cuidador');
      allow update, delete: if false;  // Solo backend
    }
    
    // Users (solo pueden leer/editar su propio perfil)
    match /users/{uid} {
      allow read: if request.auth.uid == uid || hasRole('admin');
      allow write: if request.auth.uid == uid || hasRole('admin');
      
      match /notifications/{notifId} {
        allow read, write: if request.auth.uid == uid;
      }
    }
  }
}
```

---

## Indexes Compuestos Necesarios

```javascript
// firestore.indexes.json
{
  "indexes": [
    {
      "collectionGroup": "readings",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "zone_id", "order": "ASCENDING"},
        {"fieldPath": "timestamp", "order": "DESCENDING"}
      ]
    },
    {
      "collectionGroup": "events",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "zone_id", "order": "ASCENDING"},
        {"fieldPath": "type", "order": "ASCENDING"},
        {"fieldPath": "timestamp", "order": "DESCENDING"}
      ]
    },
    {
      "collectionGroup": "density_maps",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "zone_id", "order": "ASCENDING"},
        {"fieldPath": "timestamp", "order": "DESCENDING"}
      ]
    }
  ]
}
```

---

## Queries Comunes

```javascript
// 1. Últimas 100 lecturas de una zona
const readings = await db
  .collection('spaces/space_valdivia_1/zones/zone1/readings')
  .orderBy('timestamp', 'desc')
  .limit(100)
  .get();

// 2. Eventos de riego del último mes
const riegoEvents = await db
  .collectionGroup('events')
  .where('zone_id', '==', 'zone1')
  .where('type', '==', 'riego')
  .where('timestamp', '>=', thirtyDaysAgo)
  .orderBy('timestamp', 'desc')
  .get();

// 3. Listener en tiempo real para nueva lectura
db.collection('spaces/space_valdivia_1/zones/zone1/readings')
  .orderBy('timestamp', 'desc')
  .limit(1)
  .onSnapshot(snapshot => {
    snapshot.docChanges().forEach(change => {
      if (change.type === 'added') {
        const newReading = change.doc.data();
        updateUI(newReading);
      }
    });
  });

// 4. Comandos pendientes (Pi listener)
db.collection('commands')
  .where('status', '==', 'pending')
  .onSnapshot(snapshot => {
    snapshot.docChanges().forEach(change => {
      if (change.type === 'added') {
        executeCommand(change.doc.data());
      }
    });
  });

// 5. Estadísticas de crecimiento semanal
const densityMaps = await db
  .collection('spaces/space_valdivia_1/zones/zone1/density_maps')
  .where('timestamp', '>=', startOfWeek)
  .where('timestamp', '<=', endOfWeek)
  .get();

const avgGrowth = densityMaps.docs.reduce((acc, doc) => {
  return acc + doc.data().metrics.height_avg_cm;
}, 0) / densityMaps.size;
```

---

## Cloud Functions para Triggers

```javascript
// functions/index.js
const functions = require('firebase-functions');
const admin = require('firebase-admin');

// Trigger: Nueva lectura → evaluar alertas
exports.onNewReading = functions.firestore
  .document('spaces/{spaceId}/zones/{zoneId}/readings/{timestamp}')
  .onCreate(async (snap, context) => {
    const reading = snap.data();
    const { zoneId } = context.params;
    
    // Obtener perfil de la zona
    const zoneDoc = await admin.firestore()
      .doc(`spaces/${context.params.spaceId}/zones/${zoneId}`)
      .get();
    const zone = zoneDoc.data();
    
    // Obtener umbrales del perfil
    const profileDoc = await admin.firestore()
      .doc(`profiles/${zone.profile_id}`)
      .get();
    const thresholds = profileDoc.data().thresholds;
    
    // Evaluar alertas
    const alerts = [];
    
    if (reading.sensors.temperatura > thresholds.temp_max) {
      alerts.push({
        type: 'temp_high',
        severity: 'high',
        message: `Temperatura alta: ${reading.sensors.temperatura}°C`
      });
    }
    
    if (reading.sensors.humedad < thresholds.humidity_min) {
      alerts.push({
        type: 'humidity_low',
        severity: 'medium',
        message: `Humedad baja: ${reading.sensors.humedad}%`
      });
    }
    
    // Enviar notificaciones FCM
    if (alerts.length > 0) {
      const usersSnapshot = await admin.firestore()
        .collection('users')
        .where('spaces_access', 'array-contains', context.params.spaceId)
        .get();
      
      const tokens = usersSnapshot.docs.map(doc => doc.data().fcm_token);
      
      for (const alert of alerts) {
        await admin.messaging().sendToDevice(tokens, {
          notification: {
            title: 'Alerta Verdant Canopy',
            body: alert.message
          },
          data: {
            zone_id: zoneId,
            alert_type: alert.type
          }
        });
      }
    }
  });

// Trigger: Auto-delete comandos ejecutados
exports.cleanupCommands = functions.pubsub
  .schedule('every 5 minutes')
  .onRun(async (context) => {
    const fiveMinutesAgo = admin.firestore.Timestamp.fromMillis(
      Date.now() - 5 * 60 * 1000
    );
    
    const oldCommands = await admin.firestore()
      .collection('commands')
      .where('status', '==', 'executed')
      .where('executed_at', '<', fiveMinutesAgo)
      .get();
    
    const batch = admin.firestore().batch();
    oldCommands.docs.forEach(doc => batch.delete(doc.ref));
    await batch.commit();
    
    console.log(`Deleted ${oldCommands.size} old commands`);
  });
```

---

## Estimación de Costos (Plan Spark - Gratis)

```
Lecturas por día:       288
Eventos por día:        ~10
Mapas densidad por día: 4
Comandos por día:       ~50

Total escrituras/día:   352
Límite gratis:          20,000/día

Uso:                    1.76% ✅

Lecturas por día:       ~1,000 (PWA queries)
Límite gratis:          50,000/día

Uso:                    2% ✅

Almacenamiento:
├── 1 ciclo (90 días):  ~13 MB
├── 5 ciclos:           ~65 MB
└── Límite gratis:      1 GB ✅
```

**Conclusión:** Plan Spark es más que suficiente.

---

Esta es la estructura completa de Firestore para Verdant Canopy.
