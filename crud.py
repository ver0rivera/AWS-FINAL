import random
import string
from sqlalchemy.orm import Session
import models
import schemas
from werkzeug.security import check_password_hash
import secrets
import string


def create_alumno(db: Session, alumno: schemas.AlumnoCreate):
    db_alumno = models.Alumno(**alumno.dict())
    db.add(db_alumno)
    db.commit()
    db.refresh(db_alumno)
    return db_alumno

def get_alumno(db: Session, alumno_id: int):
    return db.query(models.Alumno).filter(models.Alumno.id == alumno_id).first()

def get_alumnos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Alumno).offset(skip).limit(limit).all()

def create_profesor(db: Session, profesor: schemas.ProfesorCreate):
    db_profesor = models.Profesor(**profesor.dict())
    db.add(db_profesor)
    db.commit()
    db.refresh(db_profesor)
    return db_profesor

def get_profesor(db: Session, profesor_id: int):
    return db.query(models.Profesor).filter(models.Profesor.id == profesor_id).first()

def get_profesores(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Profesor).offset(skip).limit(limit).all()



def delete_alumno(db: Session, alumno_id: int):
    alumno = db.query(models.Alumno).filter(models.Alumno.id == alumno_id).first()
    if alumno is None:
        return None
    db.delete(alumno)
    db.commit()
    return alumno

def delete_profesor(db: Session, profesor_id: int):
    profesor = db.query(models.Profesor).filter(models.Profesor.id == profesor_id).first()
    if profesor is None:
        return None
    db.delete(profesor)
    db.commit()
    return profesor
    

def update_profesor(db: Session, profesor_id: int, profesor: schemas.ProfesorCreate):
    db_profesor = db.query(models.Profesor).filter(models.Profesor.id == profesor_id).first()
    if db_profesor:
        for key, value in profesor.dict().items():
            setattr(db_profesor, key, value)
        db.commit()
        db.refresh(db_profesor)
        return db_profesor
    else:
        return None
    
def update_alumno(db: Session, alumno_id: int, alumno: schemas.AlumnoCreate):
    db_alumno = db.query(models.Alumno).filter(models.Alumno.id == alumno_id).first()
    if db_alumno:
        for key, value in alumno.dict().items():
            setattr(db_alumno, key, value)
        db.commit()
        db.refresh(db_alumno)
        return db_alumno
    else:
        return None

def verify_alumno_password(db: Session, alumno_id: int, password: str) -> bool:
   
    alumno = db.query(models.Alumno).filter(models.Alumno.id == alumno_id).first()
    if alumno is None:
        return False
    return alumno.password == password


def generate_session_string(length=128):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for i in range(length))