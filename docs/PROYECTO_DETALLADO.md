# Documentación Detallada del Proyecto N8N Helper Service

## Índice
1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Estructura de Directorios](#estructura-de-directorios)
4. [Análisis Detallado de Archivos](#análisis-detallado-de-archivos)
5. [Dependencias y Librerías](#dependencias-y-librerías)
6. [Configuración y Despliegue](#configuración-y-despliegue)
7. [Flujo de Trabajo](#flujo-de-trabajo)
8. [API Endpoints](#api-endpoints)
9. [Modelos de Datos](#modelos-de-datos)
10. [Servicios Externos](#servicios-externos)

---

## Descripción General

**N8N Helper Service** es un microservicio diseñado para gestionar comunicaciones automatizadas y recordatorios. El sistema permite programar y ejecutar diferentes tipos de notificaciones como SMS, llamadas telefónicas con texto a voz, mensajes de WhatsApp, emails y eventos de calendario.

### Características Principales:
- ✅ **SMS**: Envío de mensajes de texto vía Twilio
- ✅ **Llamadas**: Llamadas automatizadas con texto a voz (TTS)
- ✅ **WhatsApp**: Mensajes a través de WhatsApp Business
- 🚧 **Email**: Pendiente de implementación
- 🚧 **Calendario**: Integración con calendarios pendiente

### Stack Tecnológico:
- **Backend**: FastAPI (Python 3.11)
- **Base de Datos**: PostgreSQL 15
- **Mensajería**: Twilio API
- **Contenedorización**: Docker y Docker Compose
- **Worker**: APScheduler para tareas programadas

---

## Arquitectura del Sistema

El proyecto sigue una arquitectura de microservicios con los siguientes componentes:

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│    n8n      │────▶│   FastAPI    │────▶│  PostgreSQL  │
│  Workflow   │     │     API      │     │   Database   │
└─────────────┘     └──────────────┘     └──────────────┘
                            │                      ▲
                            │                      │
                            ▼                      │
                    ┌──────────────┐               │
                    │    Worker    │───────────────┘
                    │  Scheduler   │
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   Twilio     │
                    │   Services   │
                    └──────────────┘
```

### Componentes:

1. **API REST (FastAPI)**: Recibe solicitudes de n8n para crear tareas
2. **Base de Datos (PostgreSQL)**: Almacena las tareas programadas
3. **Worker (Scheduler)**: Proceso que ejecuta tareas pendientes cada 60 segundos
4. **Servicios Externos**: Twilio para SMS, llamadas y WhatsApp

---

## Estructura de Directorios

```
reminder-project/
│
├── app/                          # Código principal de la aplicación
│   ├── __init__.py              # Marca app/ como paquete Python
│   ├── main.py                  # Punto de entrada de FastAPI
│   ├── database.py              # Configuración de SQLAlchemy
│   ├── models.py                # Modelos de base de datos
│   ├── schemas.py               # Esquemas Pydantic para validación
│   ├── crud.py                  # Operaciones CRUD
│   │
│   ├── core/                    # Configuración central
│   │   ├── __init__.py
│   │   └── config.py            # Gestión de variables de entorno
│   │
│   ├── services/                # Integraciones con servicios externos
│   │   ├── __init__.py
│   │   ├── twilio_service.py    # Integración con Twilio
│   │   ├── email_service.py     # (Vacío) Futuro servicio de email
│   │   └── calendar_service.py  # (Vacío) Futura integración calendario
│   │
│   └── worker/                  # Procesos en segundo plano
│       ├── __init__.py
│       └── scheduler.py         # Worker que ejecuta tareas programadas
│
├── docker-compose.yml           # Orquestación de contenedores
├── Dockerfile                   # Imagen Docker para la aplicación
├── requirements.txt             # Dependencias Python
├── .env.example                 # Plantilla de variables de entorno
└── LICENSE                      # Licencia BSD 3-Clause
```

---

## Análisis Detallado de Archivos

### 1. **app/main.py** (Punto de entrada principal)
```python
# Ubicación: app/main.py:1-61
```
- **Propósito**: Define la API REST con FastAPI
- **Funcionalidades**:
  - Crea las tablas en la BD al iniciar
  - Endpoint POST `/tasks/` para crear tareas
  - Endpoint GET `/` para verificar estado del servicio
  - Maneja zonas horarias UTC correctamente
  - Determina si una tarea es inmediata o programada

### 2. **app/core/config.py** (Configuración centralizada)
```python
# Ubicación: app/core/config.py
```
- **Propósito**: Gestión de configuración mediante variables de entorno
- **Características**:
  - Usa Pydantic Settings para validación
  - Carga automática desde archivo `.env`
  - Configura credenciales de Twilio
  - Define URL de base de datos
  - Singleton pattern con instancia `settings`

### 3. **app/database.py** (Conexión a base de datos)
```python
# Ubicación: app/database.py
```
- **Componentes**:
  - **engine**: Motor SQLAlchemy configurado
  - **SessionLocal**: Factory para crear sesiones
  - **Base**: Clase base para modelos declarativos
  - **get_db()**: Generador para gestión de sesiones con contexto

### 4. **app/models.py** (Modelo de datos)
```python
# Ubicación: app/models.py
```
- **Modelo Task**:
  ```
  Task:
    - id: Integer (PK, autoincrement)
    - target: String(100) - número/email destino
    - message: Text - contenido del mensaje
    - task_type: String(50) - tipo de tarea
    - scheduled_at: DateTime - hora programada UTC
    - status: String(20) - estado (pending/done/failed)
    - extra_data: JSON - datos adicionales
    - created_at: DateTime - timestamp creación
    - updated_at: DateTime - timestamp actualización
  ```

### 5. **app/schemas.py** (Validación de datos)
```python
# Ubicación: app/schemas.py
```
- **Enumeraciones**:
  - `TaskType`: call, sms, whatsapp, email, calendar_event
  - `TaskStatus`: pending, done, failed
- **Esquemas**:
  - `TaskCreate`: Para crear nuevas tareas
  - `Task`: Esquema completo con todos los campos

### 6. **app/crud.py** (Operaciones de base de datos)
```python
# Ubicación: app/crud.py
```
- **Funciones**:
  - `create_task()`: Inserta nueva tarea
  - `get_due_tasks()`: Obtiene tareas vencidas pendientes
  - `update_task_status()`: Actualiza estado de tarea

### 7. **app/services/twilio_service.py** (Integración Twilio)
```python
# Ubicación: app/services/twilio_service.py
```
- **Características**:
  - Cliente Twilio configurado con credenciales
  - `send_sms()`: Envía SMS con número específico
  - `make_call()`: Llamadas con TTS en español
  - `send_whatsapp()`: Mensajes WhatsApp Business
  - Manejo robusto de errores
  - Logging detallado

### 8. **app/worker/scheduler.py** (Procesador de tareas)
```python
# Ubicación: app/worker/scheduler.py
```
- **Funcionamiento**:
  - Bucle infinito con sleep de 60 segundos
  - Busca tareas con `scheduled_at <= now`
  - Ejecuta según tipo: SMS, llamada o WhatsApp
  - Actualiza estado a "done" o "failed"
  - Logging extensivo para debugging

### 9. **docker-compose.yml** (Orquestación)
```yaml
# Ubicación: docker-compose.yml
```
- **Servicios**:
  1. **api**: FastAPI en puerto 8000
  2. **worker**: Scheduler en segundo plano
  3. **db**: PostgreSQL 15 Alpine
- **Características**:
  - Volúmenes para persistencia y hot-reload
  - Variables de entorno desde `.env`
  - Dependencias entre servicios

### 10. **Dockerfile** (Imagen Docker)
```dockerfile
# Ubicación: Dockerfile
```
- Base: Python 3.11 slim
- Directorio trabajo: `/app`
- Instalación optimizada de dependencias
- Copia solo código necesario

---

## Dependencias y Librerías

### Dependencias principales (requirements.txt):

| Librería | Versión | Propósito |
|----------|---------|-----------|
| **fastapi** | Latest | Framework web asíncrono de alto rendimiento |
| **uvicorn[standard]** | Latest | Servidor ASGI para FastAPI |
| **sqlalchemy** | Latest | ORM para interacción con base de datos |
| **psycopg2-binary** | Latest | Driver PostgreSQL para Python |
| **pydantic** | Latest | Validación de datos y serialización |
| **pydantic-settings** | Latest | Gestión de configuración |
| **python-dotenv** | Latest | Carga de variables desde .env |
| **twilio** | Latest | SDK para servicios de Twilio |
| **apscheduler** | Latest | Programación de tareas (usado en worker) |
| **google-api-python-client** | Latest | Cliente Google API (futuro) |
| **google-auth-oauthlib** | Latest | Autenticación OAuth Google (futuro) |
| **msal** | Latest | Microsoft Authentication Library (futuro) |

### Análisis de dependencias:

1. **Core Framework**:
   - FastAPI + Uvicorn: API REST moderna y asíncrona
   - Pydantic: Validación robusta de datos

2. **Base de Datos**:
   - SQLAlchemy: ORM maduro y flexible
   - psycopg2: Driver nativo PostgreSQL

3. **Comunicaciones**:
   - Twilio: SMS, llamadas y WhatsApp

4. **Futuras integraciones**:
   - Google APIs: Calendario y Gmail
   - MSAL: Integración con Microsoft/Outlook

---

## Configuración y Despliegue

### Variables de Entorno (.env):

```bash
# Base de datos
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=taskdb
DATABASE_URL=postgresql://myuser:mypassword@db:5432/taskdb

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+15017122661
TWILIO_SMS_NUMBER=+15017122661

# Futuras integraciones
GOOGLE_CREDENTIALS_JSON=""
OUTLOOK_CLIENT_ID=""
OUTLOOK_CLIENT_SECRET=""
OUTLOOK_TENANT_ID=""
```

### Comandos de despliegue:

```bash
# Clonar repositorio
git clone <repository-url>
cd reminder-project

# Configurar variables de entorno
cp .env.example .env
# Editar .env con credenciales reales

# Construir y ejecutar
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

---

## Flujo de Trabajo

### 1. Creación de Tarea:
```
n8n → POST /tasks/ → FastAPI → Validación → Guardar en DB
```

### 2. Procesamiento de Tarea:
```
Worker → Consulta DB → Tareas vencidas → Ejecutar → Actualizar estado
```

### 3. Ejecución según tipo:
- **SMS**: worker → twilio_service.send_sms() → Twilio API
- **Llamada**: worker → twilio_service.make_call() → Twilio API + TTS
- **WhatsApp**: worker → twilio_service.send_whatsapp() → Twilio API

---

## API Endpoints

### 1. **POST /tasks/**
- **Descripción**: Crea una nueva tarea programada
- **Request Body**:
  ```json
  {
    "target": "+1234567890",
    "message": "Recordatorio: Tienes una cita mañana",
    "task_type": "sms",
    "scheduled_at": "2025-01-15T10:30:00Z",
    "extra_data": {}
  }
  ```
- **Response**: 201 Created
  ```json
  {
    "id": 1,
    "target": "+1234567890",
    "message": "Recordatorio: Tienes una cita mañana",
    "task_type": "sms",
    "scheduled_at": "2025-01-15T10:30:00Z",
    "status": "pending",
    "extra_data": {},
    "created_at": "2025-01-10T15:00:00Z",
    "updated_at": "2025-01-10T15:00:00Z"
  }
  ```

### 2. **GET /**
- **Descripción**: Verifica el estado del servicio
- **Response**: 200 OK
  ```json
  {
    "status": "N8N Helper Service is running!"
  }
  ```

---

## Modelos de Datos

### Diagrama ER:

```
┌─────────────────────────┐
│         Task            │
├─────────────────────────┤
│ id: Integer (PK)        │
│ target: String(100)     │
│ message: Text           │
│ task_type: String(50)   │
│ scheduled_at: DateTime  │
│ status: String(20)      │
│ extra_data: JSON        │
│ created_at: DateTime    │
│ updated_at: DateTime    │
└─────────────────────────┘
```

### Estados de Tarea:
- **pending**: Tarea creada, esperando ejecución
- **done**: Tarea ejecutada exitosamente
- **failed**: Error al ejecutar la tarea

### Tipos de Tarea:
- **call**: Llamada telefónica
- **sms**: Mensaje de texto
- **whatsapp**: Mensaje WhatsApp
- **email**: Correo electrónico (no implementado)
- **calendar_event**: Evento calendario (no implementado)

---

## Servicios Externos

### Twilio
- **Uso**: SMS, llamadas y WhatsApp
- **Configuración**:
  - Account SID y Auth Token
  - Números dedicados para SMS y llamadas
  - Prefijo "whatsapp:" para WhatsApp
- **Características**:
  - TTS en español para llamadas
  - Manejo de errores con reintentos
  - Logging detallado

### Futuras Integraciones:

1. **Google Services**:
   - Gmail API para emails
   - Calendar API para eventos
   - OAuth2 para autenticación

2. **Microsoft Services**:
   - Outlook para emails
   - Calendar para eventos
   - MSAL para autenticación

---

## Licencia

Este proyecto está licenciado bajo la **BSD 3-Clause License**.

**Copyright (c) 2025, Francisco-cor**

La licencia permite uso, modificación y distribución tanto en forma de código fuente como binario, con las siguientes condiciones:
1. Mantener el aviso de copyright
2. Reproducir el aviso en distribuciones binarias
3. No usar nombres para endosar productos sin permiso

---

## Notas de Desarrollo

### Mejoras Implementadas:
- ✅ Manejo correcto de zonas horarias (UTC)
- ✅ Logging extensivo para debugging
- ✅ Separación de números Twilio por servicio
- ✅ Docker Compose optimizado
- ✅ Importaciones absolutas para compatibilidad

### Pendientes:
- 🚧 Implementar servicio de email
- 🚧 Implementar integración con calendarios
- 🚧 Añadir autenticación a la API
- 🚧 Implementar reintentos automáticos
- 🚧 Añadir métricas y monitoreo
- 🚧 Crear tests unitarios y de integración

### Consideraciones de Seguridad:
- Las credenciales se manejan via variables de entorno
- No se exponen logs con información sensible
- La base de datos está aislada en la red Docker
- Se recomienda HTTPS para producción