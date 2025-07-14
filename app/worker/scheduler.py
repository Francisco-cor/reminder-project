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
                    event_data = task.extra_data or {}
                    start_time = datetime.fromisoformat(event_data.get('start_time'))
                    end_time = datetime.fromisoformat(event_data.get('end_time'))
                    timezone = event_data.get('timezone', 'UTC')

                    result = google_calendar_service.create_event(
                        summary=event_data.get('summary', 'Evento sin título'),
                        description=event_data.get('description', task.message),
                        start_time=start_time,
                        end_time=end_time,
                        attendees=event_data.get('attendees', [task.target]),
                        location=event_data.get('location'),
                        reminder_minutes=event_data.get('reminder_minutes', [30, 10]),
                        timezone=timezone
                    )

                    if event_data.get('send_email_notification', False):
                        email_body = f"""
                        <h2>Nuevo evento agendado: {event_data.get('summary', 'Evento sin título')}</h2>
                        <p><strong>Fecha y hora:</strong> {start_time.strftime('%d/%m/%Y %H:%M')} - {end_time.strftime('%H:%M')} ({timezone})</p>
                        <p><strong>Descripción:</strong> {event_data.get('description', task.message)}</p>
                        """
                        if event_data.get('location'):
                            email_body += f"<p><strong>Ubicación:</strong> {event_data.get('location')}</p>"
                        if event_data.get('additional_email_body'):
                            email_body += f"<br/>{event_data.get('additional_email_body')}"
                        email_body += f'''
                        <br/>
                        <p>Se ha agregado este evento a tu calendario de Google. Recibirás recordatorios 30 y 10 minutos antes del evento.</p>
                        <p><a href="{result.get('htmlLink')}">Ver evento en Google Calendar</a></p>
                        '''
                        for attendee_email in event_data.get('attendees', [task.target]):
                            try:
                                email_service.send_email(
                                    to_email=attendee_email,
                                    subject=f"Invitación: {event_data.get('summary', 'Evento sin título')}",
                                    body=email_body
                                )
                            except Exception as e:
                                print(f"Error al enviar correo a {attendee_email}: {e}")

                elif task.task_type == TaskType.outlook_event:
                    event_data = task.extra_data or {}
                    start_time = datetime.fromisoformat(event_data.get('start_time'))
                    end_time = datetime.fromisoformat(event_data.get('end_time'))
                    timezone = event_data.get('timezone', 'UTC')

                    result = outlook_calendar_service.create_outlook_event(
                        subject=event_data.get('subject', 'Evento sin título'),
                        body=event_data.get('body', task.message),
                        start_time=start_time,
                        end_time=end_time,
                        attendees=event_data.get('attendees', [task.target]),
                        location=event_data.get('location'),
                        is_online_meeting=event_data.get('is_online_meeting', False),
                        reminder_minutes_before_start=event_data.get('reminder_minutes_before_start', 15),
                        categories=event_data.get('categories'),
                        importance=event_data.get('importance', 'normal'),
                        timezone=timezone
                    )

                    if event_data.get('send_email_notification', False):
                        email_body = f"""
                        <h2>Nuevo evento agendado: {event_data.get('subject', 'Evento sin título')}</h2>
                        <p><strong>Fecha y hora:</strong> {start_time.strftime('%d/%m/%Y %H:%M')} - {end_time.strftime('%H:%M')} ({timezone})</p>
                        <p><strong>Descripción:</strong></p>
                        <div style="margin-left: 20px;">{event_data.get('body', task.message)}</div>
                        """
                        if event_data.get('location'):
                            email_body += f"<p><strong>Ubicación:</strong> {event_data.get('location')}</p>"
                        if event_data.get('is_online_meeting') and result.get('onlineMeeting'):
                            join_url = result['onlineMeeting'].get('joinUrl', '')
                            if join_url:
                                email_body += f'<p><strong>Unirse a la reunión:</strong> <a href="{join_url}">Click aquí para unirse a Teams</a></p>'
                        if event_data.get('additional_email_content'):
                            email_body += f"<br/><h3>Información adicional:</h3>{event_data.get('additional_email_content')}"
                        email_body += f"""
                        <br/>
                        <p>Se ha agregado este evento a tu calendario de Outlook. Recibirás un recordatorio {event_data.get('reminder_minutes_before_start', 15)} minutos antes del evento.</p>
                        <p><a href="{result.get('webLink')}">Ver evento en Outlook</a></p>
                        """
                        for attendee_email in event_data.get('attendees', [task.target]):
                            try:
                                email_service.send_email(
                                    to_email=attendee_email,
                                    subject=f"Confirmación: {event_data.get('subject', 'Evento sin título')}",
                                    body=email_body
                                )
                            except Exception as e:
                                print(f"Error al enviar correo adicional a {attendee_email}: {e}")

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