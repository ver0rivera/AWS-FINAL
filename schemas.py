from typing import Optional
from pydantic import BaseModel

class AlumnoBase(BaseModel):
    nombres: str
    apellidos: str
    matricula: str
    promedio: float
    imagen: Optional[str] = None
    password: str
    

class AlumnoCreate(AlumnoBase):
    pass

class Alumno(AlumnoBase):
    id: int

    class Config:
        orm_mode = True

class ProfesorBase(BaseModel):
    numeroEmpleado: int
    nombres: str
    apellidos: str
    horasClase: int

class ProfesorCreate(ProfesorBase):
    pass

class Profesor(ProfesorBase):
    id: int

    class Config:
        orm_mode = True

class ValidacionContraseña(BaseModel):
    password: str

class ValidacionSesion(BaseModel):
    sessionString: str