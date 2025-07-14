# Ejemplos de uso de Outlook Calendar API

## Configuración requerida en .env

```
OUTLOOK_TENANT_ID=tu-tenant-id
OUTLOOK_CLIENT_ID=tu-client-id
OUTLOOK_CLIENT_SECRET=tu-client-secret
OUTLOOK_SENDER_EMAIL=email@tudominio.com
```

## 1. Crear un evento con reunión de Teams y notificación por email

```bash
curl -X POST "http://localhost:8000/outlook/calendar/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Reunión de equipo - Teams",
    "body": "<h3>Agenda de la reunión</h3><ul><li>Revisión de avances</li><li>Planificación Q1</li><li>Preguntas y respuestas</li></ul>",
    "start_time": "2024-01-15T10:00:00",
    "end_time": "2024-01-15T11:00:00",
    "attendees": ["usuario1@empresa.com", "usuario2@empresa.com"],
    "location": "Microsoft Teams",
    "is_online_meeting": true,
    "send_email_notification": true,
    "reminder_minutes_before_start": 30,
    "categories": ["Trabajo", "Importante"],
    "importance": "high",
    "additional_email_content": "<p><strong>Preparación:</strong></p><ul><li>Revisar el reporte mensual</li><li>Preparar preguntas</li></ul>"
  }'
```

## 2. Crear un evento presencial sin notificación adicional

```bash
curl -X POST "http://localhost:8000/outlook/calendar/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Almuerzo de trabajo",
    "body": "Discutir nueva propuesta de proyecto",
    "start_time": "2024-01-16T13:00:00",
    "end_time": "2024-01-16T14:30:00",
    "attendees": ["cliente@empresa.com"],
    "location": "Restaurante La Plaza, Centro",
    "is_online_meeting": false,
    "send_email_notification": false,
    "reminder_minutes_before_start": 60,
    "importance": "normal"
  }'
```

## 3. Programar un evento para ser creado en el futuro

```bash
curl -X POST "http://localhost:8000/outlook/calendar/events/schedule/?scheduled_at=2024-01-25T08:00:00" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Presentación trimestral",
    "body": "<h2>Resultados Q4 2023</h2><p>Presentación de resultados financieros y operativos</p>",
    "start_time": "2024-02-01T09:00:00",
    "end_time": "2024-02-01T10:30:00",
    "attendees": ["director@empresa.com", "gerentes@empresa.com", "inversionistas@empresa.com"],
    "location": "Auditorio principal",
    "is_online_meeting": false,
    "send_email_notification": true,
    "categories": ["Presentaciones", "Q4"],
    "importance": "high",
    "additional_email_content": "<p>Por favor confirmar asistencia. Los materiales se compartirán 24 horas antes.</p>"
  }'
```

## 4. Verificar disponibilidad de múltiples personas

```bash
curl -X POST "http://localhost:8000/outlook/calendar/schedule/free-busy/" \
  -H "Content-Type: application/json" \
  -d '{
    "emails": ["persona1@empresa.com", "persona2@empresa.com", "persona3@empresa.com"],
    "start_time": "2024-01-15T08:00:00",
    "end_time": "2024-01-15T18:00:00",
    "interval_minutes": 30
  }'
```

## 5. Listar eventos próximos

```bash
curl -X GET "http://localhost:8000/outlook/calendar/events/?top=20"
```

## 6. Buscar eventos por texto

```bash
curl -X GET "http://localhost:8000/outlook/calendar/events/?search=presentación&top=10"
```

## 7. Listar eventos en un rango de fechas

```bash
curl -X GET "http://localhost:8000/outlook/calendar/events/?start_datetime=2024-01-15T00:00:00&end_datetime=2024-01-31T23:59:59&top=50"
```

## 8. Actualizar un evento existente

```bash
curl -X PUT "http://localhost:8000/outlook/calendar/events/{event_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Reunión de equipo - ACTUALIZADA",
    "start_time": "2024-01-15T14:00:00",
    "end_time": "2024-01-15T15:00:00",
    "location": "Sala B - Piso 3"
  }'
```

## 9. Cancelar un evento con notificación

```bash
curl -X DELETE "http://localhost:8000/outlook/calendar/events/{event_id}?send_cancellation=true"
```

## 10. Programar evento como tarea (usando el endpoint de tareas)

```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "organizador@empresa.com",
    "message": "Evento programado de Outlook",
    "task_type": "outlook_event",
    "scheduled_at": "2024-01-20T08:00:00",
    "extra_data": {
      "subject": "Capacitación mensual",
      "body": "<h3>Temas a cubrir:</h3><ul><li>Nuevas políticas</li><li>Actualizaciones de sistemas</li><li>Q&A</li></ul>",
      "start_time": "2024-01-25T15:00:00",
      "end_time": "2024-01-25T17:00:00",
      "attendees": ["equipo.ventas@empresa.com", "equipo.soporte@empresa.com"],
      "location": "Sala de capacitación",
      "is_online_meeting": true,
      "send_email_notification": true,
      "reminder_minutes_before_start": 45,
      "categories": ["Capacitación", "Mensual"],
      "importance": "normal",
      "additional_email_content": "<p><strong>Material requerido:</strong> Laptop con acceso a los sistemas internos</p>"
    }
  }'
```

## Características especiales de Outlook:

1. **Reuniones de Teams**: Cuando `is_online_meeting` es `true`, se crea automáticamente una reunión de Microsoft Teams con link de acceso.

2. **Categorías**: Puedes asignar múltiples categorías a los eventos para mejor organización.

3. **Importancia**: Los eventos pueden marcarse como `low`, `normal` o `high`.

4. **Free/Busy**: El endpoint de disponibilidad permite verificar los horarios libres de múltiples personas para encontrar el mejor momento para una reunión.

5. **Integración con email**: Los eventos de Outlook se integran perfectamente con el sistema de correo, enviando:
   - Invitación de calendario automática (manejada por Outlook)
   - Correo personalizado adicional opcional con información extra

6. **Recordatorios**: A diferencia de Google Calendar que permite múltiples recordatorios, Outlook usa un único recordatorio especificado en minutos antes del evento.

## Notas importantes:

- Los permisos necesarios en Azure AD incluyen: `Calendars.ReadWrite`, `Mail.Send`
- La zona horaria está configurada como `America/Mexico_City`
- Las invitaciones de calendario se envían automáticamente a menos que se cancele el evento
- Los eventos con Teams incluyen el link de reunión en el campo `onlineMeeting.joinUrl`