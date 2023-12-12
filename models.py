from sqlalchemy import Column, Integer, String, Float
from database import Base

class Alumno(Base):
    __tablename__ = 'alumnos'
    id = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(255))
    apellidos = Column(String(255))
    matricula = Column(String(255), unique=True)
    promedio = Column(Float)
    imagen = Column(String(255))
    password = Column(String(500))

class Profesor(Base):
    __tablename__ = 'profesores'
    id = Column(Integer, primary_key=True, index=True)
    numeroEmpleado = Column(String(255), unique=True)
    nombres = Column(String(255))
    apellidos = Column(String(255))
    horasClase = Column(Integer)
