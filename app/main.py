from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone # <-- CORRECCIÓN 1: Se importa timezone

# Importaciones absolutas para compatibilidad con Docker y Uvicorn
import crud
import models
import schemas
from database import engine, get_db
from services import twilio_service

# Esta línea asegura que las tablas se creen al iniciar la API.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="N8N Helper Service",
    description="Un microservicio para manejar comunicaciones y recordatorios."
)

@app.post("/tasks/", response_model=schemas.Task, status_code=201)
def schedule_or_run_task(
    task: schemas.TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Recibe una tarea desde n8n. Toda la lógica interna se maneja en UTC.
    """
    # CORRECCIÓN 2: Usamos datetime.now(timezone.utc) para obtener la hora
    # actual en un formato "aware" (consciente de la zona horaria).
    now_utc = datetime.now(timezone.utc)
    
    # Comprobamos si la hora programada ya pasó o está en el próximo minuto.
    # Ahora la comparación es entre dos fechas "aware", lo cual es correcto.
    is_immediate = task.scheduled_at <= (now_utc + timedelta(seconds=65))

    if is_immediate:
        print(f"Tarea inmediata recibida: {task.task_type} a {task.target}")
    else:
        print(f"Tarea programada recibida para {task.scheduled_at.isoformat()}")

    # La función create_task se encarga de guardar la nueva tarea en la BBDD.
    return crud.create_task(db=db, task=task)

@app.get("/")
def read_root():
    """Endpoint raíz para verificar que el servicio está activo."""
    return {"status": "N8N Helper Service is running!"}


# La función de ayuda que tenías es útil para el futuro, la conservamos.
# No se usa por ahora, pero podría ser activada con BackgroundTasks.
def execute_task(task_data: schemas.TaskCreate):
    """Función que ejecuta la acción real de la tarea."""
    if task_data.task_type == schemas.TaskType.call:
        print("Realizando llamada...")
        # twilio_service.make_call(to_number=task_data.target, message=task_data.message)
    elif task_data.task_type == schemas.TaskType.sms:
        print("Enviando SMS...")
        # twilio_service.send_sms(to_number=task_data.target, message=task_data.message)
    # ... agregar lógica para otros tipos de tarea