from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    call = "call"
    sms = "sms"
    whatsapp = "whatsapp"
    email = "email"
    calendar_event = "calendar_event"

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