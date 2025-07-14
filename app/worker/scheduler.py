import time
from sqlalchemy.orm import Session
from datetime import datetime


import sys
import os

from database import engine
import models

from database import SessionLocal
from crud import get_due_tasks, update_task_status
from schemas import TaskType, TaskStatus
from services import twilio_service, email_service
from services import google_calendar_service, outlook_calendar_service

# Asegura que las tablas existan
models.Base.metadata.create_all(bind=engine)

def process_pending_tasks():
    # Usamos flush=True para forzar la salida inmediata en los logs de Docker
    print(f"[{datetime.utcnow()}] Worker: Buscando tareas pendientes...", flush=True)
    db: Session = SessionLocal()
    try:
        due_tasks = get_due_tasks(db)
        if not due_tasks:
            print("Worker: No hay tareas pendientes.", flush=True)
            return

        print(f"Worker: Se encontraron {len(due_tasks)} tareas para procesar.", flush=True)

        for task in due_tasks:
            print(f"Worker: Procesando tarea ID {task.id} ({task.task_type})", flush=True)
            try:
                if task.task_type == TaskType.sms:
                    twilio_service.send_sms(to_number=task.target, message=task.message)
                elif task.task_type == TaskType.call:
                    twilio_service.make_call(to_number=task.target, message=task.message)
                elif task.task_type == TaskType.whatsapp:
                    twilio_service.send_whatsapp(to_number=task.target, message=task.message)
                elif task.task_type == TaskType.email:
                    subject = task.extra_data.get('subject', 'Recordatorio del Sistema')
                    email_service.send_email(
                        to_email=task.target, 
                        subject=subject, 
                        body=task.message
                    )
                elif task.task_type == TaskType.calendar_event:
                    # Extraer datos del evento desde extra_data
                    event_data = task.extra_data or {}
                    
                    # Si send_email_notification es True, usar la función combinada
                    if event_data.get('send_email_notification', False):
                        google_calendar_service.create_event_with_email_notification(
                            summary=event_data.get('summary', 'Evento sin título'),
                            description=event_data.get('description', task.message),
                            start_time=event_data.get('start_time', task.scheduled_at),
                            end_time=event_data.get('end_time', task.scheduled_at),
                            attendees=event_data.get('attendees', [task.target]),
                            location=event_data.get('location'),
                            additional_email_body=event_data.get('additional_email_body')
                        )
                    else:
                        # Crear solo el evento de calendario
                        google_calendar_service.create_event(
                            summary=event_data.get('summary', 'Evento sin título'),
                            description=event_data.get('description', task.message),
                            start_time=event_data.get('start_time', task.scheduled_at),
                            end_time=event_data.get('end_time', task.scheduled_at),
                            attendees=event_data.get('attendees', [task.target]),
                            location=event_data.get('location'),
                            reminder_minutes=event_data.get('reminder_minutes', [30, 10])
                        )
                elif task.task_type == TaskType.outlook_event:
                    # Extraer datos del evento de Outlook desde extra_data
                    event_data = task.extra_data or {}
                    
                    # Convertir strings ISO a datetime si es necesario
                    start_time = event_data.get('start_time', task.scheduled_at)
                    end_time = event_data.get('end_time', task.scheduled_at)
                    
                    if isinstance(start_time, str):
                        start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    if isinstance(end_time, str):
                        end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    
                    # Si send_email_notification es True, usar la función combinada
                    if event_data.get('send_email_notification', False):
                        outlook_calendar_service.create_outlook_event_with_email(
                            subject=event_data.get('subject', 'Evento sin título'),
                            body=event_data.get('body', task.message),
                            start_time=start_time,
                            end_time=end_time,
                            attendees=event_data.get('attendees', [task.target]),
                            location=event_data.get('location'),
                            is_online_meeting=event_data.get('is_online_meeting', False),
                            additional_email_content=event_data.get('additional_email_content'),
                            categories=event_data.get('categories')
                        )
                    else:
                        # Crear solo el evento de Outlook
                        outlook_calendar_service.create_outlook_event(
                            subject=event_data.get('subject', 'Evento sin título'),
                            body=event_data.get('body', task.message),
                            start_time=start_time,
                            end_time=end_time,
                            attendees=event_data.get('attendees', [task.target]),
                            location=event_data.get('location'),
                            is_online_meeting=event_data.get('is_online_meeting', False),
                            reminder_minutes_before_start=event_data.get('reminder_minutes_before_start', 15),
                            categories=event_data.get('categories'),
                            importance=event_data.get('importance', 'normal')
                        )

                print(f"Worker: Tarea ID {task.id} completada exitosamente.", flush=True)
                update_task_status(db, task.id, TaskStatus.done)

            except Exception as e:
                # Esta es la línea clave que queremos ver
                print(f"Worker: ERROR al procesar tarea ID {task.id}. Error: {e}", flush=True)
                update_task_status(db, task.id, TaskStatus.failed)
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando Worker de Tareas 'Ruidoso'...", flush=True)
    while True:
        process_pending_tasks()
        time.sleep(60)