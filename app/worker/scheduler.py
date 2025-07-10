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
from services import twilio_service, email_service, calendar_service

models.Base.metadata.create_all(bind=engine)

def process_pending_tasks():
    """
    Función principal del worker. Obtiene y procesa tareas pendientes.
    """
    print(f"[{datetime.utcnow()}] Worker: Buscando tareas pendientes...")
    db: Session = SessionLocal()
    try:
        due_tasks = get_due_tasks(db)
        if not due_tasks:
            print("Worker: No hay tareas pendientes.")
            return

        print(f"Worker: Se encontraron {len(due_tasks)} tareas para procesar.")
        
        for task in due_tasks:
            print(f"Worker: Procesando tarea ID {task.id} ({task.task_type})")
            try:
                # Lógica para ejecutar la tarea según su tipo
                if task.task_type == TaskType.call:
                    twilio_service.make_call(to_number=task.target, message=task.message)
                
                elif task.task_type == TaskType.sms:
                    twilio_service.send_sms(to_number=task.target, message=task.message)

                elif task.task_type == TaskType.whatsapp:
                    twilio_service.send_whatsapp(to_number=task.target, message=task.message)
                
                # Aquí agregarías las llamadas a email_service y calendar_service
                
                print(f"Worker: Tarea ID {task.id} completada exitosamente.")
                update_task_status(db, task.id, TaskStatus.done)

            except Exception as e:
                print(f"Worker: ERROR al procesar tarea ID {task.id}. Error: {e}")
                update_task_status(db, task.id, TaskStatus.failed)

    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando Worker de Tareas...")
    while True:
        process_pending_tasks()
        # Esperar 60 segundos antes de la siguiente verificación
        time.sleep(60)