from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from schemas import (
    OutlookEventCreate,
    OutlookEventUpdate,
    OutlookEventResponse,
    FreeBusyRequest,
    TaskCreate,
    TaskType,
    Task
)
from services import outlook_calendar_service, email_service
import crud

router = APIRouter(
    prefix="/outlook/calendar",
    tags=["outlook-calendar"],
    responses={404: {"description": "Not found"}},
)

@router.post("/events/", response_model=OutlookEventResponse, status_code=201)
def create_outlook_event(
    event: OutlookEventCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un evento inmediato en Outlook Calendar.
    Si send_email_notification es True, también envía un correo personalizado.
    Si is_online_meeting es True, crea una reunión de Teams.
    """
    try:
        result = outlook_calendar_service.create_outlook_event(
            subject=event.subject,
            body=event.body,
            start_time=event.start_time,
            end_time=event.end_time,
            attendees=event.attendees,
            location=event.location,
            is_online_meeting=event.is_online_meeting,
            reminder_minutes_before_start=event.reminder_minutes_before_start,
            categories=event.categories,
            importance=event.importance,
            timezone=event.timezone
        )

        if event.send_email_notification:
            email_body = f"""
            <h2>Nuevo evento agendado: {event.subject}</h2>
            <p><strong>Fecha y hora:</strong> {event.start_time.strftime('%d/%m/%Y %H:%M')} - {event.end_time.strftime('%H:%M')} ({event.timezone})</p>
            <p><strong>Descripción:</strong></p>
            <div style="margin-left: 20px;">{event.body}</div>
            """
            if event.location:
                email_body += f"<p><strong>Ubicación:</strong> {event.location}</p>"
            if event.is_online_meeting and result.get('onlineMeeting'):
                join_url = result['onlineMeeting'].get('joinUrl', '')
                if join_url:
                    email_body += f'<p><strong>Unirse a la reunión:</strong> <a href="{join_url}">Click aquí para unirse a Teams</a></p>'
            if event.additional_email_content:
                email_body += f"<br/><h3>Información adicional:</h3>{event.additional_email_content}"
            email_body += f"""
            <br/>
            <p>Se ha agregado este evento a tu calendario de Outlook. Recibirás un recordatorio {event.reminder_minutes_before_start} minutos antes del evento.</p>
            <p><a href="{result.get('webLink')}">Ver evento en Outlook</a></p>
            """
            for attendee_email in event.attendees:
                try:
                    email_service.send_email(
                        to_email=attendee_email,
                        subject=f"Confirmación: {event.subject}",
                        body=email_body
                    )
                except Exception as e:
                    print(f"Error al enviar correo adicional a {attendee_email}: {e}")

        return OutlookEventResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/schedule/", response_model=Task, status_code=201)
def schedule_outlook_event(
    event: OutlookEventCreate,
    scheduled_at: datetime,
    db: Session = Depends(get_db)
):
    """
    Programa un evento de Outlook para ser creado en el futuro.
    El evento se creará automáticamente en la fecha y hora especificada.
    """
    # Crear una tarea de tipo outlook_event
    task_data = TaskCreate(
        target=event.attendees[0] if event.attendees else "system",
        message=event.body,
        task_type=TaskType.outlook_event,
        scheduled_at=scheduled_at,
        extra_data={
            "subject": event.subject,
            "body": event.body,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "attendees": event.attendees,
            "location": event.location,
            "timezone": event.timezone,
            "is_online_meeting": event.is_online_meeting,
            "send_email_notification": event.send_email_notification,
            "reminder_minutes_before_start": event.reminder_minutes_before_start,
            "categories": event.categories,
            "importance": event.importance,
            "additional_email_content": event.additional_email_content
        }
    )
    
    return crud.create_task(db=db, task=task_data)

@router.get("/events/{event_id}", response_model=OutlookEventResponse)
def get_outlook_event(event_id: str):
    """
    Obtiene un evento específico de Outlook Calendar por su ID.
    """
    try:
        event = outlook_calendar_service.get_outlook_event(event_id)
        return OutlookEventResponse(**event)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/events/{event_id}", response_model=OutlookEventResponse)
def update_outlook_event(
    event_id: str,
    event_update: OutlookEventUpdate
):
    """
    Actualiza un evento existente en Outlook Calendar.
    """
    try:
        # Preparar solo los campos que no son None
        update_data = {k: v for k, v in event_update.dict(exclude_unset=True).items()}
        
        result = outlook_calendar_service.update_outlook_event(
            event_id=event_id,
            **update_data
        )
        
        return OutlookEventResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/events/{event_id}", status_code=204)
def delete_outlook_event(
    event_id: str,
    send_cancellation: bool = Query(True, description="Enviar notificación de cancelación a los asistentes")
):
    """
    Elimina (cancela) un evento de Outlook Calendar.
    """
    try:
        outlook_calendar_service.delete_outlook_event(
            event_id=event_id,
            send_cancellation=send_cancellation
        )
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/", response_model=List[OutlookEventResponse])
def list_outlook_events(
    start_datetime: Optional[datetime] = Query(None, description="Fecha/hora de inicio"),
    end_datetime: Optional[datetime] = Query(None, description="Fecha/hora de fin"),
    top: int = Query(10, ge=1, le=100, description="Número máximo de resultados"),
    search: Optional[str] = Query(None, description="Texto de búsqueda")
):
    """
    Lista eventos del calendario de Outlook con filtros opcionales.
    """
    try:
        events = outlook_calendar_service.list_outlook_events(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            top=top,
            search=search
        )
        
        # Convertir cada evento al formato de respuesta
        return [OutlookEventResponse(**event) for event in events]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedule/free-busy/")
def get_free_busy_schedule(request: FreeBusyRequest):
    """
    Obtiene la disponibilidad (libre/ocupado) de múltiples usuarios.
    Útil para encontrar horarios disponibles para reuniones.
    """
    try:
        result = outlook_calendar_service.get_free_busy_schedule(
            emails=request.emails,
            start_time=request.start_time,
            end_time=request.end_time,
            interval_minutes=request.interval_minutes,
            timezone=request.timezone
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))