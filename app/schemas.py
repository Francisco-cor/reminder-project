from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    call = "call"
    sms = "sms"
    whatsapp = "whatsapp"
    email = "email"
    calendar_event = "calendar_event"
    outlook_event = "outlook_event"

class TaskStatus(str, Enum):
    pending = "pending"
    done = "done"
    failed = "failed"

class TaskCreate(BaseModel):
    target: str = Field(..., example="+1234567890")
    message: str = Field(..., example="Recordatorio: Sacar la comida del horno.")
    task_type: TaskType
    scheduled_at: datetime = Field(default_factory=datetime.utcnow, description="Fecha y hora UTC para ejecutar la tarea.")
    extra_data: Optional[Dict[str, Any]] = None # Para datos adicionales como el título de un evento de calendario

class Task(TaskCreate):
    id: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CalendarEventCreate(BaseModel):
    summary: str = Field(..., example="Reunión de equipo")
    description: str = Field(..., example="Revisión semanal del proyecto")
    start_time: datetime = Field(..., example="2024-01-15T10:00:00")
    end_time: datetime = Field(..., example="2024-01-15T11:00:00")
    attendees: List[str] = Field(..., example=["usuario1@example.com", "usuario2@example.com"])
    location: Optional[str] = Field(None, example="Sala de conferencias A")
    timezone: str = Field("UTC", example="America/Mexico_City", description="Zona horaria del evento")
    send_email_notification: bool = Field(True, description="Enviar notificación por email además de la invitación de calendario")
    reminder_minutes: Optional[List[int]] = Field([30, 10], example=[30, 10])
    additional_email_body: Optional[str] = Field(None, example="Por favor traer laptop y documentos del proyecto")

class CalendarEventUpdate(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    attendees: Optional[List[str]] = None
    location: Optional[str] = None
    timezone: Optional[str] = Field(None, example="America/Bogota", description="Zona horaria del evento")
    send_notifications: bool = True

class CalendarEventResponse(BaseModel):
    id: str
    summary: str
    description: Optional[str]
    start: Dict[str, Any]
    end: Dict[str, Any]
    attendees: Optional[List[Dict[str, str]]]
    location: Optional[str]
    htmlLink: str
    status: str

class OutlookEventCreate(BaseModel):
    subject: str = Field(..., example="Reunión de equipo")
    body: str = Field(..., example="<p>Revisión semanal del proyecto</p>")
    start_time: datetime = Field(..., example="2024-01-15T10:00:00")
    end_time: datetime = Field(..., example="2024-01-15T11:00:00")
    attendees: List[str] = Field(..., example=["usuario1@example.com", "usuario2@example.com"])
    location: Optional[str] = Field(None, example="Sala de conferencias A")
    timezone: str = Field("UTC", example="America/Mexico_City", description="Zona horaria del evento")
    is_online_meeting: bool = Field(False, description="Crear reunión de Teams")
    send_email_notification: bool = Field(True, description="Enviar correo adicional personalizado")
    reminder_minutes_before_start: int = Field(15, example=15)
    categories: Optional[List[str]] = Field(None, example=["Trabajo", "Importante"])
    importance: str = Field("normal", example="normal", description="low, normal, high")
    additional_email_content: Optional[str] = Field(None, example="<p>Por favor traer laptop</p>")

class OutlookEventUpdate(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    attendees: Optional[List[str]] = None
    location: Optional[str] = None
    timezone: Optional[str] = Field(None, example="America/Bogota", description="Zona horaria del evento")

class OutlookEventResponse(BaseModel):
    id: str
    subject: str
    bodyPreview: Optional[str]
    start: Dict[str, Any]
    end: Dict[str, Any]
    location: Optional[Dict[str, str]]
    attendees: Optional[List[Dict[str, Any]]]
    webLink: str
    onlineMeeting: Optional[Dict[str, Any]]
    isOnlineMeeting: Optional[bool]
    categories: Optional[List[str]]
    importance: str

class FreeBusyRequest(BaseModel):
    emails: List[str] = Field(..., example=["usuario1@example.com", "usuario2@example.com"])
    start_time: datetime = Field(..., example="2024-01-15T08:00:00")
    end_time: datetime = Field(..., example="2024-01-15T18:00:00")
    interval_minutes: int = Field(30, example=30)
    timezone: str = Field("UTC", example="America/Mexico_City", description="Zona horaria para la consulta")