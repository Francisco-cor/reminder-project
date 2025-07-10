from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from . import crud, models, schemas
from .database import engine, get_db
from .services import twilio_service # Importarás los otros servicios aquí

# Crea las tablas en la base de datos al iniciar (si no existen)
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
    Recibe una tarea desde n8n.
    - Si la tarea es para "ahora", la ejecuta inmediatamente en segundo plano.
    - Si la tarea está programada para el futuro, la guarda en la BBDD.
    """
    # Si la tarea es para dentro de los próximos 65 segundos, la ejecutamos ya mismo
    is_immediate = task.scheduled_at <= (datetime.utcnow() + timedelta(seconds=65))

    if is_immediate:
        # Lógica para ejecución inmediata en segundo plano
        # Esto libera a n8n para que no tenga que esperar
        print(f"Tarea inmediata recibida: {task.task_type} a {task.target}")
        
        # Aquí puedes añadir la tarea a una cola de fondo
        # background_tasks.add_task(execute_task, task)
        # Por ahora, simplemente la guardamos y el worker la recogerá en el siguiente ciclo
        
        return crud.create_task(db=db, task=task)

    else:
        # Lógica para guardar tarea programada
        print(f"Tarea programada recibida para {task.scheduled_at}")
        return crud.create_task(db=db, task=task)

@app.get("/")
def read_root():
    return {"status": "N8N Helper Service is running!"}

# Función de ayuda (aún no usada en el endpoint, pero útil para el futuro)
def execute_task(task_data: schemas.TaskCreate):
    """Función que ejecuta la acción real de la tarea."""
    if task_data.task_type == schemas.TaskType.call:
        print("Realizando llamada...")
        # twilio_service.make_call(to_number=task_data.target, message=task_data.message)
    elif task_data.task_type == schemas.TaskType.sms:
        print("Enviando SMS...")
        # twilio_service.send_sms(to_number=task_data.target, message=task_data.message)
    # ... agregar lógica para otros tipos de tarea