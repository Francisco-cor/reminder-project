# Ejemplos de uso de Google Calendar API

## Configuración requerida en .env

```
GOOGLE_CREDENTIALS_JSON=/path/to/your/google-credentials.json
```

## 1. Crear un evento inmediato con notificación por email

```bash
curl -X POST "http://localhost:8000/calendar/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Reunión de equipo",
    "description": "Revisión semanal del proyecto",
    "start_time": "2024-01-15T10:00:00",
    "end_time": "2024-01-15T11:00:00",
    "attendees": ["usuario1@example.com", "usuario2@example.com"],
    "location": "Sala de conferencias A",
    "send_email_notification": true,
    "reminder_minutes": [30, 10],
    "additional_email_body": "<p>Por favor traer laptop y documentos del proyecto.</p><p>Agenda: <ul><li>Revisión de avances</li><li>Próximos pasos</li></ul></p>"
  }'
```

## 2. Crear un evento sin notificación adicional por email

```bash
curl -X POST "http://localhost:8000/calendar/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Llamada con cliente",
    "description": "Discutir requisitos del nuevo proyecto",
    "start_time": "2024-01-16T15:00:00",
    "end_time": "2024-01-16T16:00:00",
    "attendees": ["cliente@empresa.com"],
    "send_email_notification": false,
    "reminder_minutes": [15]
  }'
```

## 3. Programar un evento para ser creado en el futuro

```bash
curl -X POST "http://localhost:8000/calendar/events/schedule/" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Presentación de resultados",
    "description": "Presentación trimestral de resultados",
    "start_time": "2024-02-01T09:00:00",
    "end_time": "2024-02-01T10:30:00",
    "attendees": ["director@empresa.com", "equipo@empresa.com"],
    "location": "Auditorio principal",
    "send_email_notification": true,
    "additional_email_body": "Se compartirán los resultados del Q4 2023"
  }' \
  -G --data-urlencode "scheduled_at=2024-01-25T08:00:00"
```

## 4. Listar eventos próximos

```bash
curl -X GET "http://localhost:8000/calendar/events/?max_results=20"
```

## 5. Buscar eventos por texto

```bash
curl -X GET "http://localhost:8000/calendar/events/?query=reunion&max_results=10"
```

## 6. Actualizar un evento existente

```bash
curl -X PUT "http://localhost:8000/calendar/events/{event_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Reunión de equipo - POSPUESTA",
    "start_time": "2024-01-15T14:00:00",
    "end_time": "2024-01-15T15:00:00",
    "send_notifications": true
  }'
```

## 7. Eliminar un evento

```bash
curl -X DELETE "http://localhost:8000/calendar/events/{event_id}?send_notifications=true"
```

## 8. Programar evento como tarea (usando el endpoint existente de tareas)

```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "organizador@empresa.com",
    "message": "Evento programado",
    "task_type": "calendar_event",
    "scheduled_at": "2024-01-20T08:00:00",
    "extra_data": {
      "summary": "Revisión mensual",
      "description": "Revisión de métricas y objetivos del mes",
      "start_time": "2024-01-25T10:00:00",
      "end_time": "2024-01-25T11:30:00",
      "attendees": ["equipo1@empresa.com", "equipo2@empresa.com"],
      "location": "Oficina principal",
      "send_email_notification": true,
      "reminder_minutes": [60, 30, 10],
      "additional_email_body": "Por favor revisar el dashboard antes de la reunión"
    }
  }'
```

## Notas importantes:

1. **Autenticación**: Asegúrate de que el archivo de credenciales de Google (`GOOGLE_CREDENTIALS_JSON`) tenga los permisos necesarios para Google Calendar API.

2. **Zona horaria**: Los tiempos están configurados para usar `America/Mexico_City`. Puedes modificar esto en `google_calendar_service.py`.

3. **Calendario**: Por defecto se usa el calendario 'primary'. Puedes especificar otro calendario usando el parámetro `calendar_id`.

4. **Notificaciones**: 
   - Las invitaciones de calendario se envían automáticamente por Google
   - Si `send_email_notification` es `true`, se envía un correo adicional personalizado usando el servicio de email configurado (Microsoft Graph)

5. **Recordatorios**: Se pueden configurar múltiples recordatorios en minutos antes del evento. Por defecto son 30 y 10 minutos.

6. **Permisos necesarios en Google Cloud**:
   - Google Calendar API habilitada
   - Cuenta de servicio con permisos de Calendar
   - Si usas un calendario compartido, la cuenta de servicio debe tener permisos de editor