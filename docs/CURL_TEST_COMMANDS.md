# Comandos CURL para probar la API

## 🔧 Base URL
```
BASE_URL=http://localhost:8000
```

## 📧 Ejemplos de Email (Microsoft Outlook)

### 1. Enviar email inmediato
```bash
curl -X POST "$BASE_URL/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "emilianoa.aguilar17@gmail.com",
    "message": "<h2>Hola</h2><p>Este es un correo de prueba enviado desde el sistema.</p><p>Saludos,<br>El equipo</p>",
    "task_type": "email",
    "scheduled_at": "2025-07-14T12:38:00",
    "extra_data": {
      "subject": "Correo de prueba - Sistema de notificaciones"
    }
  }'
```

### 2. Programar email para el futuro
```bash
curl -X POST "$BASE_URL/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "cliente@empresa.com",
    "message": "<h2>Recordatorio importante</h2><p>Le recordamos que su cita está programada para mañana.</p><ul><li>Fecha: 16 de enero</li><li>Hora: 10:00 AM</li><li>Lugar: Oficina principal</li></ul>",
    "task_type": "email",
    "scheduled_at": "2024-01-15T08:00:00",
    "extra_data": {
      "subject": "Recordatorio de cita - Mañana 10:00 AM"
    }
  }'
```

## 📅 Ejemplos de Google Calendar

### 1. Crear evento inmediato con notificación
```bash
curl -X POST "$BASE_URL/calendar/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Reunión de proyecto - Sprint Planning",
    "description": "Planificación del próximo sprint del proyecto XYZ",
    "start_time": "2024-01-16T09:00:00",
    "end_time": "2024-01-16T10:30:00",
    "attendees": ["equipo1@empresa.com", "equipo2@empresa.com"],
    "location": "Sala de reuniones A",
    "send_email_notification": true,
    "reminder_minutes": [30, 10],
    "additional_email_body": "<p><strong>Por favor preparar:</strong></p><ul><li>Lista de tareas pendientes</li><li>Estimaciones de tiempo</li><li>Bloqueos identificados</li></ul>"
  }'
```

### 2. Programar evento de Google Calendar para el futuro
```bash
curl -X POST "$BASE_URL/calendar/events/schedule/?scheduled_at=2024-01-20T08:00:00" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Presentación mensual de resultados",
    "description": "Revisión de métricas y KPIs del mes",
    "start_time": "2024-02-01T11:00:00",
    "end_time": "2024-02-01T12:00:00",
    "attendees": ["gerencia@empresa.com", "finanzas@empresa.com"],
    "location": "Auditorio",
    "send_email_notification": true,
    "additional_email_body": "<p>Se compartirá el dashboard 30 minutos antes de la reunión.</p>"
  }'
```

### 3. Listar eventos de Google Calendar
```bash
curl -X GET "$BASE_URL/calendar/events/?max_results=10"
```

### 4. Buscar eventos en Google Calendar
```bash
curl -X GET "$BASE_URL/calendar/events/?query=reunion&max_results=5"
```

## 📘 Ejemplos de Outlook Calendar

### 1. Crear evento con Teams meeting
```bash
curl -X POST "$BASE_URL/outlook/calendar/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Kick-off proyecto ABC",
    "body": "<h3>Agenda</h3><ol><li>Introducción y objetivos</li><li>Alcance del proyecto</li><li>Timeline y entregables</li><li>Asignación de responsabilidades</li><li>Q&A</li></ol>",
    "start_time": "2024-01-17T14:00:00",
    "end_time": "2024-01-17T15:30:00",
    "attendees": ["cliente@empresa.com", "pm@empresa.com", "tech-lead@empresa.com"],
    "location": "Microsoft Teams",
    "is_online_meeting": true,
    "send_email_notification": true,
    "reminder_minutes_before_start": 45,
    "categories": ["Proyectos", "Cliente ABC"],
    "importance": "high",
    "additional_email_content": "<p><strong>Documentos adjuntos:</strong></p><ul><li>Propuesta técnica</li><li>Cronograma tentativo</li><li>Presupuesto</li></ul><p>Los documentos se enviarán por separado 1 hora antes de la reunión.</p>"
  }'
```

### 2. Crear evento presencial
```bash
curl -X POST "$BASE_URL/outlook/calendar/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Comida con cliente potencial",
    "body": "Reunión informal para discutir oportunidades de colaboración",
    "start_time": "2024-01-18T13:00:00",
    "end_time": "2024-01-18T14:30:00",
    "attendees": ["prospecto@otraempresa.com"],
    "location": "Restaurante El Mesón, Av. Principal 123",
    "is_online_meeting": false,
    "send_email_notification": false,
    "reminder_minutes_before_start": 120,
    "categories": ["Ventas", "Networking"],
    "importance": "normal"
  }'
```

### 3. Verificar disponibilidad
```bash
curl -X POST "$BASE_URL/outlook/calendar/schedule/free-busy/" \
  -H "Content-Type: application/json" \
  -d '{
    "emails": ["persona1@empresa.com", "persona2@empresa.com", "persona3@empresa.com"],
    "start_time": "2024-01-22T08:00:00",
    "end_time": "2024-01-22T18:00:00",
    "interval_minutes": 30
  }'
```

### 4. Listar eventos de Outlook
```bash
curl -X GET "$BASE_URL/outlook/calendar/events/?top=10"
```

### 5. Buscar eventos en Outlook
```bash
curl -X GET "$BASE_URL/outlook/calendar/events/?search=proyecto&top=5"
```

### 6. Eventos en rango de fechas
```bash
curl -X GET "$BASE_URL/outlook/calendar/events/?start_datetime=2024-01-15T00:00:00&end_datetime=2024-01-31T23:59:59"
```

## 📱 Otros tipos de tareas

### SMS
```bash
curl -X POST "$BASE_URL/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "+521234567890",
    "message": "Recordatorio: Su cita es mañana a las 10:00 AM. Para confirmar responda SI.",
    "task_type": "sms",
    "scheduled_at": "2024-01-15T08:00:00"
  }'
```

### Llamada
```bash
curl -X POST "$BASE_URL/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "+521234567890",
    "message": "Este es un recordatorio automático. Su pago vence mañana. Para más información, comuníquese al 01800-123-4567.",
    "task_type": "call",
    "scheduled_at": "2024-01-15T10:00:00"
  }'
```

### WhatsApp
```bash
curl -X POST "$BASE_URL/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "+521234567890",
    "message": "¡Hola! 👋 Le recordamos que su pedido está listo para recoger. Horario de atención: 9 AM - 6 PM.",
    "task_type": "whatsapp",
    "scheduled_at": "2024-01-15T09:00:00"
  }'
```

## 🔄 Actualizar y eliminar eventos

### Actualizar evento de Google Calendar
```bash
curl -X PUT "$BASE_URL/calendar/events/{event_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Reunión POSPUESTA - Sprint Planning",
    "start_time": "2024-01-16T14:00:00",
    "end_time": "2024-01-16T15:30:00",
    "location": "Sala B",
    "send_notifications": true
  }'
```

### Eliminar evento de Google Calendar
```bash
curl -X DELETE "$BASE_URL/calendar/events/{event_id}?send_notifications=true"
```

### Actualizar evento de Outlook
```bash
curl -X PUT "$BASE_URL/outlook/calendar/events/{event_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Kick-off proyecto ABC - CAMBIO DE HORA",
    "start_time": "2024-01-17T16:00:00",
    "end_time": "2024-01-17T17:30:00"
  }'
```

### Cancelar evento de Outlook
```bash
curl -X DELETE "$BASE_URL/outlook/calendar/events/{event_id}?send_cancellation=true"
```

## 📝 Notas importantes:

1. **Fechas**: Asegúrate de usar fechas futuras para las pruebas
2. **Emails**: Reemplaza los emails de ejemplo con direcciones reales
3. **IDs de eventos**: Después de crear un evento, usa el ID retornado para actualizar/eliminar
4. **Zona horaria**: Las fechas están en formato ISO 8601, ajusta según tu zona horaria
5. **Autenticación**: Asegúrate de que las credenciales en `.env` estén correctamente configuradas

## 🚀 Inicio rápido

1. **Verificar que el servicio está activo:**
   ```bash
   curl $BASE_URL/
   ```

2. **Crear un evento de prueba en Outlook (recomendado para empezar):**
   ```bash
   curl -X POST "$BASE_URL/outlook/calendar/events/" \
     -H "Content-Type: application/json" \
     -d '{
       "subject": "Evento de prueba",
       "body": "Este es un evento de prueba del sistema",
       "start_time": "2024-01-15T15:00:00",
       "end_time": "2024-01-15T16:00:00",
       "attendees": ["tu-email@empresa.com"],
       "send_email_notification": true,
       "importance": "normal"
     }'
   ```