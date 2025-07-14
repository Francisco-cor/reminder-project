# Comandos CURL para Probar la API (Actualizado)

Este archivo contiene ejemplos de comandos `curl` para probar todos los endpoints de la API, incluyendo los cambios recientes de zona horaria y la refactorización del envío de correos.

## 🔧 Configuración Base
```bash
# Define la URL base de tu API
BASE_URL="http://localhost:8000"

# Define un email de prueba para los asistentes
TEST_EMAIL="tu_email_de_prueba@example.com"

# Define un ID de evento de Google y Outlook para pruebas (reemplázalos con IDs reales después de crear un evento)
GOOGLE_EVENT_ID="google_event_id_a_reemplazar"
OUTLOOK_EVENT_ID="outlook_event_id_a_reemplazar"
```

---

## 📅 Google Calendar

### 1. Crear Evento Inmediato
Crea un evento en Google Calendar y envía una notificación por correo electrónico.
```bash
curl -X POST "$BASE_URL/calendar/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Reunión de Sincronización (Google)",
    "description": "Revisión semanal de avances y bloqueos.",
    "start_time": "2025-08-15T10:00:00",
    "end_time": "2025-08-15T11:00:00",
    "attendees": ["'"$TEST_EMAIL"'"],
    "location": "Oficina Principal, Sala 101",
    "timezone": "America/Mexico_City",
    "send_email_notification": true,
    "reminder_minutes": [30, 10],
    "additional_email_body": "<p>Por favor, tener listos los reportes de la semana.</p>"
  }'
```

### 2. Programar Creación de Evento
Agenda una tarea para que un evento de Google Calendar se cree en el futuro.
```bash
curl -X POST "$BASE_URL/calendar/events/schedule/?scheduled_at=2025-08-14T18:00:00Z" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Lanzamiento de Producto (Google)",
    "description": "Evento de lanzamiento para el nuevo producto.",
    "start_time": "2025-09-01T12:00:00",
    "end_time": "2025-09-01T13:00:00",
    "attendees": ["'"$TEST_EMAIL"'", "marketing@example.com"],
    "location": "Centro de Convenciones",
    "timezone": "America/New_York",
    "send_email_notification": true
  }'
```3

### 3. Obtener un Evento Específico
```bash
curl -X GET "$BASE_URL/calendar/events/'"$GOOGLE_EVENT_ID"'"
```

### 4. Actualizar un Evento
Cambia la hora y la zona horaria de un evento existente.
```bash
curl -X PUT "$BASE_URL/calendar/events/'"$GOOGLE_EVENT_ID"'" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Reunión de Sincronización (Google) - Reprogramada",
    "start_time": "2025-08-15T14:30:00",
    "end_time": "2025-08-15T15:30:00",
    "timezone": "America/Bogota"
  }'
```

### 5. Listar Eventos
```bash
curl -X GET "$BASE_URL/calendar/events/?max_results=5"
```

### 6. Eliminar un Evento
```bash
curl -X DELETE "$BASE_URL/calendar/events/'"$GOOGLE_EVENT_ID"'"
```

---

## 📘 Outlook Calendar

### 1. Crear Evento Inmediato con Reunión de Teams
Crea un evento en Outlook con un enlace de Teams y envía un correo de notificación.
```bash
curl -X POST "$BASE_URL/outlook/calendar/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Discusión Técnica (Outlook)",
    "body": "<p>Análisis de la nueva arquitectura de microservicios.</p>",
    "start_time": "2025-08-16T15:00:00",
    "end_time": "2025-08-16T16:30:00",
    "attendees": ["'"$TEST_EMAIL"'", "dev-team@example.com"],
    "location": "Microsoft Teams",
    "timezone": "Europe/Madrid",
    "is_online_meeting": true,
    "send_email_notification": true,
    "reminder_minutes_before_start": 60,
    "categories": ["Técnico", "Arquitectura"],
    "importance": "high"
  }'
```

### 2. Programar Creación de Evento
```bash
curl -X POST "$BASE_URL/outlook/calendar/events/schedule/?scheduled_at=2025-08-15T10:00:00Z" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Capacitación de Personal (Outlook)",
    "body": "<p>Sesión de capacitación sobre el nuevo software de CRM.</p>",
    "start_time": "2025-08-20T09:00:00",
    "end_time": "2025-08-20T11:00:00",
    "attendees": ["'"$TEST_EMAIL"'", "ventas@example.com"],
    "location": "Sala de Capacitación 2",
    "timezone": "America/Mexico_City",
    "send_email_notification": false
  }'
```

### 3. Obtener un Evento Específico
```bash
curl -X GET "$BASE_URL/outlook/calendar/events/'"$OUTLOOK_EVENT_ID"'"
```

### 4. Actualizar un Evento
```bash
curl -X PUT "$BASE_URL/outlook/calendar/events/'"$OUTLOOK_EVENT_ID"'" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Discusión Técnica (Outlook) - Actualizada",
    "location": "Sala de Proyectos 3",
    "timezone": "Europe/Paris"
  }'
```

### 5. Consultar Disponibilidad (Free/Busy)
Verifica la disponibilidad de varios usuarios en una zona horaria específica.
```bash
curl -X POST "$BASE_URL/outlook/calendar/schedule/free-busy/" \
  -H "Content-Type: application/json" \
  -d '{
    "emails": ["'"$TEST_EMAIL"'", "otro_colega@example.com"],
    "start_time": "2025-08-18T09:00:00",
    "end_time": "2025-08-18T18:00:00",
    "interval_minutes": 60,
    "timezone": "America/Argentina/Buenos_Aires"
  }'
```

### 6. Eliminar un Evento
```bash
curl -X DELETE "$BASE_URL/outlook/calendar/events/'"$OUTLOOK_EVENT_ID"'"
```

---

## ✅ Tareas Genéricas (SMS, Llamada, Email)

### 1. Programar un SMS
```bash
curl -X POST "$BASE_URL/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "+15551234567",
    "message": "Recordatorio: Su cita de servicio es mañana a las 9:00 AM.",
    "task_type": "sms",
    "scheduled_at": "2025-08-19T14:00:00Z"
  }'
```

### 2. Programar una Llamada
```bash
curl -X POST "$BASE_URL/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "+15551234568",
    "message": "Hola. Este es un recordatorio de que su pago está programado para mañana. Gracias.",
    "task_type": "call",
    "scheduled_at": "2025-08-19T15:00:00Z"
  }'
```

### 3. Programar un Email Genérico
```bash
curl -X POST "$BASE_URL/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "'"$TEST_EMAIL"'",
    "message": "<h1>Confirmación de Pedido</h1><p>Su pedido #12345 ha sido enviado.</p>",
    "task_type": "email",
    "scheduled_at": "2025-08-19T16:00:00Z",
    "extra_data": {
      "subject": "Confirmación de Envío - Pedido #12345"
    }
  }'
```

---

## 📝 Notas
*   **Fechas y Horas**: Todas las fechas y horas deben estar en formato ISO 8601 (`YYYY-MM-DDTHH:MM:SS`). Para `scheduled_at`, se recomienda usar el sufijo `Z` para indicar UTC.
*   **Zona Horaria**: El campo `timezone` es crucial para que los eventos se muestren correctamente en los calendarios. Usa identificadores de la base de datos IANA (ej. `America/New_York`, `Europe/London`).
*   **IDs de Eventos**: Después de crear un evento, la respuesta de la API incluirá un `id`. Copia y pega este ID en las variables `GOOGLE_EVENT_ID` u `OUTLOOK_EVENT_ID` para probar las operaciones de actualización y eliminación.

