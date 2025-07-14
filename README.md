# 📅 Sistema de Notificaciones y Gestión de Eventos

Un microservicio completo para manejar comunicaciones multicanal (Email, SMS, WhatsApp, llamadas) y gestión de eventos de calendario (Google Calendar y Outlook/Microsoft 365). Diseñado para integrarse fácilmente con n8n u otros sistemas de automatización.

## 🌟 Características principales

### 📧 Comunicaciones
- **Email**: Envío a través de Microsoft Graph API (Outlook/Office 365)
- **SMS**: Integración con Twilio
- **WhatsApp**: Mensajería vía Evolution API
- **Llamadas**: Llamadas automatizadas con Twilio

### 📅 Gestión de Calendarios
- **Google Calendar**: Creación, actualización y eliminación de eventos
- **Outlook Calendar**: Gestión completa de eventos y reuniones de Teams
- **Notificaciones duales**: Invitaciones de calendario + correos personalizados
- **Verificación de disponibilidad**: Free/Busy para múltiples usuarios

### ⏰ Sistema de Tareas
- Programación de tareas futuras
- Worker con procesamiento automático cada minuto
- Estados de tareas: pending, done, failed
- Soporte para ejecución inmediata o programada

## 🏗️ Arquitectura

```
reminder-project/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── crud.py                 # Database operations
│   ├── database.py             # Database connection
│   ├── core/
│   │   └── config.py           # Settings management
│   ├── services/
│   │   ├── email_service.py            # Microsoft Graph email
│   │   ├── google_calendar_service.py  # Google Calendar
│   │   ├── outlook_calendar_service.py # Outlook Calendar
│   │   ├── twilio_service.py           # SMS/Calls
│   │   └── whatsapp_service.py         # WhatsApp
│   ├── routers/
│   │   ├── calendar_router.py          # Google Calendar endpoints
│   │   └── outlook_calendar_router.py  # Outlook Calendar endpoints
│   └── worker/
│       └── scheduler.py        # Background task processor
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # API container
├── worker.Dockerfile           # Worker container
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Docker y Docker Compose
- Cuenta de Microsoft Azure con app registrada
- Cuenta de servicio de Google Cloud
- Cuenta de Twilio (opcional)
- Evolution API configurada (opcional)

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd reminder-project
```

### 2. Configurar variables de entorno
Copia el archivo de ejemplo y configura tus credenciales:
```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:
```env
# Base de datos
DATABASE_URL=postgresql://user:password@db:5432/reminder_agenda
POSTGRES_DB=reminder_agenda
POSTGRES_USER=user
POSTGRES_PASSWORD=password

# Microsoft Graph (Outlook/Teams)
OUTLOOK_TENANT_ID=tu-tenant-id
OUTLOOK_CLIENT_ID=tu-client-id
OUTLOOK_CLIENT_SECRET=tu-client-secret
OUTLOOK_SENDER_EMAIL=sender@tudominio.com

# Google Calendar
GOOGLE_CREDENTIALS_JSON=./gdc.json

# Twilio (opcional)
TWILIO_ACCOUNT_SID=tu-account-sid
TWILIO_AUTH_TOKEN=tu-auth-token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_SMS_NUMBER=+1234567890

# Evolution API (opcional)
EVOLUTION_API_URL=https://tu-evolution-api.com
EVOLUTION_API_INSTANCE=tu-instancia
EVOLUTION_API_KEY=tu-api-key
```

### 3. Configurar Google Calendar
1. Crea una cuenta de servicio en Google Cloud Console
2. Habilita Google Calendar API
3. Descarga el archivo JSON de credenciales
4. Colócalo en la raíz del proyecto como `gdc.json`

### 4. Configurar Microsoft Graph
1. Registra una aplicación en Azure Portal
2. Configura los permisos: `Calendars.ReadWrite`, `Mail.Send`
3. Crea un secreto de cliente
4. Copia el Tenant ID, Client ID y Client Secret al `.env`

### 5. Iniciar los servicios
```bash
docker-compose up -d
```

Esto iniciará:
- API en `http://localhost:8000`
- PostgreSQL en puerto 5432
- Worker de procesamiento de tareas
- PgAdmin en `http://localhost:5050` (opcional)

## 📖 Uso de la API

### Documentación interactiva
Accede a la documentación Swagger en: `http://localhost:8000/docs`

### Ejemplos rápidos

#### 1. Enviar un email
```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "destinatario@example.com",
    "message": "<h2>Hola</h2><p>Este es un correo de prueba.</p>",
    "task_type": "email",
    "scheduled_at": "2024-01-14T12:00:00",
    "extra_data": {
      "subject": "Correo de prueba"
    }
  }'
```

#### 2. Crear evento en Outlook con Teams
```bash
curl -X POST "http://localhost:8000/outlook/calendar/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Reunión de equipo",
    "body": "<p>Agenda de la reunión</p>",
    "start_time": "2024-01-15T10:00:00",
    "end_time": "2024-01-15T11:00:00",
    "attendees": ["persona1@empresa.com", "persona2@empresa.com"],
    "is_online_meeting": true,
    "timezone": "America/Mexico_City"
  }'
```

#### 3. Crear evento en Google Calendar
```bash
curl -X POST "http://localhost:8000/calendar/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Sprint Planning",
    "description": "Planificación del sprint",
    "start_time": "2024-01-16T09:00:00",
    "end_time": "2024-01-16T10:30:00",
    "attendees": ["equipo@empresa.com"],
    "timezone": "America/Mexico_City"
  }'
```

#### 4. Verificar disponibilidad (Outlook)
```bash
curl -X POST "http://localhost:8000/outlook/calendar/schedule/free-busy/" \
  -H "Content-Type: application/json" \
  -d '{
    "emails": ["persona1@empresa.com", "persona2@empresa.com"],
    "start_time": "2024-01-15T08:00:00",
    "end_time": "2024-01-15T18:00:00",
    "timezone": "America/Mexico_City"
  }'
```

## 📚 Endpoints principales

### Tareas generales
- `POST /tasks/` - Crear tarea (email, sms, call, whatsapp, calendar_event, outlook_event)
- `GET /` - Verificar estado del servicio

### Google Calendar
- `POST /calendar/events/` - Crear evento inmediato
- `POST /calendar/events/schedule/` - Programar evento futuro
- `GET /calendar/events/` - Listar eventos
- `GET /calendar/events/{id}` - Obtener evento específico
- `PUT /calendar/events/{id}` - Actualizar evento
- `DELETE /calendar/events/{id}` - Eliminar evento

### Outlook Calendar
- `POST /outlook/calendar/events/` - Crear evento inmediato
- `POST /outlook/calendar/events/schedule/` - Programar evento futuro
- `POST /outlook/calendar/schedule/free-busy/` - Verificar disponibilidad
- `GET /outlook/calendar/events/` - Listar eventos
- `GET /outlook/calendar/events/{id}` - Obtener evento específico
- `PUT /outlook/calendar/events/{id}` - Actualizar evento
- `DELETE /outlook/calendar/events/{id}` - Eliminar evento

## 🔧 Configuración avanzada

### Zonas horarias
El sistema soporta zonas horarias configurables para cada evento. Por defecto usa UTC, pero puedes especificar cualquier zona horaria válida:
- `America/Mexico_City`
- `America/New_York`
- `Europe/Madrid`
- `Asia/Tokyo`

### Worker de tareas
El worker revisa cada 60 segundos las tareas pendientes y las ejecuta. Para cambiar el intervalo, modifica `worker/scheduler.py`:

```python
if __name__ == "__main__":
    print("Iniciando Worker de Tareas...", flush=True)
    while True:
        process_pending_tasks()
        time.sleep(60)  # Cambiar aquí el intervalo en segundos
```

### Logs y debugging
Los logs del worker y la API están disponibles mediante:
```bash
# Logs de la API
docker-compose logs -f api

# Logs del worker
docker-compose logs -f worker

# Todos los logs
docker-compose logs -f
```

## 🧪 Testing

### Pruebas manuales
Usa los archivos incluidos:
- `CURL_TEST_COMMANDS.md` - Comandos curl listos para usar
- `API_TEST_EXAMPLES.json` - Ejemplos JSON para cada endpoint

### Verificar conexiones
```bash
# Verificar base de datos
docker-compose exec api python -c "from database import engine; print('DB OK')"

# Verificar servicios
curl http://localhost:8000/
```

## 🐛 Solución de problemas

### Error de conexión a base de datos
```bash
# Reiniciar contenedores
docker-compose restart

# Verificar logs de PostgreSQL
docker-compose logs db
```

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código cerrado y no está disponible para distribución pública.