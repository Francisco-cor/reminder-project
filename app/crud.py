from sqlalchemy.orm import Session
import models
import schemas
from datetime import datetime, timedelta

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_due_tasks(db: Session):
    now = datetime.utcnow()
    # Busca tareas pendientes cuya hora programada esté en el pasado o en el próximo minuto
    return db.query(models.Task).filter(
        models.Task.status == schemas.TaskStatus.pending,
        models.Task.scheduled_at <= now
    ).all()

def update_task_status(db: Session, task_id: int, status: schemas.TaskStatus):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db_task.status = status
        db.commit()
        db.refresh(db_task)
    return db_task