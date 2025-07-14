from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from schemas import (
    CalendarEventCreate, 
    CalendarEventUpdate, 
    CalendarEventResponse,
    TaskCreate,
    TaskType,
    Task
)
from services import google_calendar_service, email_service
import crud

router = APIRouter(
    prefix="/calendar",
    tags=["calendar"],
    responses={404: {"description": "Not found"}},
)

@router.post("/events/", response_model=CalendarEventResponse, status_code=201)
def create_calendar_event(
    event: CalendarEventCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un evento inmediato en Google Calendar.
    Si send_email_notification es True, también envía un correo personalizado.
    """
    try:
        result = google_calendar_service.create_event(
            summary=event.summary,
            description=event.description,
            start_time=event.start_time,
            end_time=event.end_time,
            attendees=event.attendees,
            location=event.location,
            reminder_minutes=event.reminder_minutes,
            timezone=event.timezone
        )

        if event.send_email_notification:
            email_body = f'''
            <h2>Nuevo evento agendado: {event.summary}</h2>
            <p><strong>Fecha y hora:</strong> {event.start_time.strftime('%d/%m/%Y %H:%M')} - {event.end_time.strftime('%H:%M')} ({event.timezone})</p>
            <p><strong>Descripción:</strong> {event.description}</p>
            '''
            if event.location:
                email_body += f"<p><strong>Ubicación:</strong> {event.location}</p>"
            if event.additional_email_body:
                email_body += f"<br/>{event.additional_email_body}"
            email_body += f'''
            <br/>
            <p>Se ha agregado este evento a tu calendario de Google. Recibirás recordatorios 30 y 10 minutos antes del evento.</p>
            <p><a href="{result.get('htmlLink')}">Ver evento en Google Calendar</a></p>
            '''
            for attendee_email in event.attendees:
                try:
                    email_service.send_email(
                        to_email=attendee_email,
                        subject=f"Invitación: {event.summary}",
                        body=email_body
                    )
                except Exception as e:
                    print(f"Error al enviar correo a {attendee_email}: {e}")

        return CalendarEventResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/schedule/", response_model=Task, status_code=201)
def schedule_calendar_event(
    event: CalendarEventCreate,
    scheduled_at: datetime,
    db: Session = Depends(get_db)
):
    """
    Programa un evento de calendario para ser creado en el futuro.
    El evento se creará automáticamente en la fecha y hora especificada.
    """
    # Crear una tarea de tipo calendar_event
    task_data = TaskCreate(
        target=event.attendees[0] if event.attendees else "system",
        message=event.description,
        task_type=TaskType.calendar_event,
        scheduled_at=scheduled_at,
        extra_data={
            "summary": event.summary,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "attendees": event.attendees,
            "location": event.location,
            "timezone": event.timezone,
            "send_email_notification": event.send_email_notification,
            "reminder_minutes": event.reminder_minutes,
            "additional_email_body": event.additional_email_body
        }
    )
    
    return crud.create_task(db=db, task=task_data)

@router.get("/events/{event_id}", response_model=CalendarEventResponse)
def get_calendar_event(
    event_id: str,
    calendar_id: str = Query("primary", description="ID del calendario")
):
    """
    Obtiene un evento específico de Google Calendar por su ID.
    """
    try:
        event = google_calendar_service.get_event(event_id, calendar_id)
        return CalendarEventResponse(**event)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/events/{event_id}", response_model=CalendarEventResponse)
def update_calendar_event(
    event_id: str,
    event_update: CalendarEventUpdate,
    calendar_id: str = Query("primary", description="ID del calendario")
):
    """
    Actualiza un evento existente en Google Calendar.
    """
    try:
        # Preparar solo los campos que no son None
        update_data = {k: v for k, v in event_update.dict(exclude_unset=True).items()}
        
        result = google_calendar_service.update_event(
            event_id=event_id,
            calendar_id=calendar_id,
            **update_data
        )
        
        return CalendarEventResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/events/{event_id}", status_code=204)
def delete_calendar_event(
    event_id: str,
    calendar_id: str = Query("primary", description="ID del calendario"),
    send_notifications: bool = Query(True, description="Enviar notificaciones a los asistentes")
):
    """
    Elimina un evento de Google Calendar.
    """
    try:
        google_calendar_service.delete_event(
            event_id=event_id,
            calendar_id=calendar_id,
            send_notifications=send_notifications
        )
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/", response_model=List[CalendarEventResponse])
def list_calendar_events(
    time_min: Optional[datetime] = Query(None, description="Fecha/hora mínima"),
    time_max: Optional[datetime] = Query(None, description="Fecha/hora máxima"),
    max_results: int = Query(10, ge=1, le=100, description="Número máximo de resultados"),
    query: Optional[str] = Query(None, description="Texto de búsqueda"),
    calendar_id: str = Query("primary", description="ID del calendario")
):
    """
    Lista eventos del calendario con filtros opcionales.
    """
    try:
        events = google_calendar_service.list_events(
            time_min=time_min,
            time_max=time_max,
            max_results=max_results,
            calendar_id=calendar_id,
            query=query
        )
        
        return [CalendarEventResponse(**event) for event in events]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))