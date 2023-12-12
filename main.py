import time
from typing import List
import uuid
from fastapi import Body, FastAPI, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import crud
import models
import schemas
import database
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
import boto3
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv





models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
load_dotenv()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_session_token = os.getenv("AWS_SESSION_TOKEN")  # Omitir si no es necesario# Omitir si no es necesario
      

dynamodb = boto3.resource("dynamodb",
                    aws_access_key_id= aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_session_token = aws_session_token,
                    region_name=("us-east-1"))

table = dynamodb.Table('sesiones-alumnos')





@app.exception_handler(RequestValidationError)
async def standard_validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )
    
app.add_exception_handler(RequestValidationError,standard_validation_exception_handler)

# Endpoints para Alumnos
@app.get("/alumnos", response_model=List[schemas.Alumno])
def get_alumnos(db: Session = Depends(get_db)):
    return crud.get_alumnos(db)

@app.get("/alumnos/{alumno_id}", response_model=schemas.Alumno)
def get_alumno(alumno_id: int, db: Session = Depends(get_db)):
    alumno = crud.get_alumno(db, alumno_id)
    if alumno is None:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno

@app.post("/alumnos", response_model=schemas.Alumno, status_code=status.HTTP_201_CREATED)
def create_alumno(alumno: schemas.AlumnoCreate, db: Session = Depends(get_db)):
    return crud.create_alumno(db, alumno)

@app.put("/alumnos/{alumno_id}", response_model=schemas.Alumno)
def update_alumno(alumno_id: int, alumno: schemas.AlumnoCreate, db: Session = Depends(get_db)):
    updated_alumno = crud.update_alumno(db, alumno_id, alumno)
    if updated_alumno is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alumno no encontrado")
    return updated_alumno


@app.delete("/alumnos/{alumno_id}", response_model=schemas.Alumno)
def delete_alumno(alumno_id: int, db: Session = Depends(get_db)):
    alumno_eliminado = crud.delete_alumno(db, alumno_id)
    if alumno_eliminado is None:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno_eliminado

# Endpoints para Profesores
@app.get("/profesores", response_model=List[schemas.Profesor])
def get_profesores(db: Session = Depends(get_db)):
    return crud.get_profesores(db)

@app.get("/profesores/{profesor_id}", response_model=schemas.Profesor)
def get_profesor(profesor_id: int, db: Session = Depends(get_db)):
    profesor = crud.get_profesor(db, profesor_id)
    if profesor is None:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor

@app.post("/profesores", response_model=schemas.Profesor, status_code=status.HTTP_201_CREATED)
def create_profesor(profesor: schemas.ProfesorCreate, db: Session = Depends(get_db)):
    return crud.create_profesor(db, profesor)

@app.put("/profesores/{profesor_id}", response_model=schemas.Profesor)
def update_profesor(profesor_id: int, profesor: schemas.ProfesorCreate, db: Session = Depends(get_db)):
    return crud.update_profesor(db, profesor_id, profesor)

@app.put("/profesores/{profesor_id}", response_model=schemas.Profesor)
def update_profesor(profesor_id: int, profesor: schemas.ProfesorCreate, db: Session = Depends(get_db)):
    # Verificar si el profesor existe
    existing_profesor = crud.get_profesor(db, profesor_id)
    if not existing_profesor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesor no encontrado")
    updated_profesor = crud.update_profesor(db, profesor_id, profesor)
    return updated_profesor

@app.delete("/profesores/{profesor_id}", response_model=schemas.Profesor)
def delete_profesor(profesor_id: int, db: Session = Depends(get_db)):
    profesor_eliminado = crud.delete_profesor(db, profesor_id)
    if profesor_eliminado is None:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor_eliminado


#Probar el bucket


@app.post("/alumnos/{id}/fotoPerfil")
async def upload_foto_perfil(id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # Obtener las credenciales y el nombre del bucket de las variables de entorno
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_session_token = os.getenv("AWS_SESSION_TOKEN")  # Omitir si no es necesario# Omitir si no es necesario
        s3_bucket_name = ("projectbucket.mx")

        # Configura el cliente de S3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token  # Omitir si no es necesario
        )
        print('esta leyendo el bucket')
        # Sube el archivo a S3
        file_content = await file.read()
        s3_client.put_object(
            Bucket=s3_bucket_name,
            Key=file.filename,
            Body=file_content,
            ACL='public-read'
        )
         
        # Construye la URL del archivo
        file_url = f"https://{s3_bucket_name}.s3.amazonaws.com/{file.filename}"
        print('se deberia haber creado el archivo')
        # Actualiza la URL en la base de datos
        alumno = crud.get_alumno(db, id)
        if not alumno:
            raise HTTPException(status_code=404, detail="Alumno no encontrado")
        alumno.imagen = file_url  # Asegúrate de que el campo se llama 'imagen' en tu modelo
        db.commit()
        print('chupo faros')
        return {"fotoPerfilUrl": file_url}

    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Error al subir el archivo")



#DINAMO

@app.post("/alumnos/{id}/session/login")
async def login(id: int, password: schemas.ValidacionContraseña, db: Session = Depends(get_db)):
    # Verificar la contraseña del alumno
    if not crud.verify_alumno_password(db, id, password.password):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

   
    # Si la contraseña es correcta, crea una sesión
    #session_string = str(uuid.uuid4()) 
    sessionString = crud.generate_session_string()
    timestamp = int(time.time())  # Timestamp actual

    # Escribe en DynamoDB
    table.put_item(
        Item={
            'id': sessionString,
            'fecha': timestamp,
            'alumnoId': id,
            'active': True,
            'sessionString': sessionString
        }
    )

    return {"sessionString": sessionString}



@app.post("/alumnos/{id}/session/verify")
async def verify_session(id: int, sessionString: schemas.ValidacionSesion):
    response = table.get_item(
        Key = {
            'id': sessionString.sessionString,
            'alumnoId': id
        }
    )
    print('RESPONSE')
    print(response)

    item = response.get('Item')
    print('ITEM')
    print(item)
    if item and item['active'] and item['alumnoId'] == id:
        return {"message": "Sesión válida"}
    else:
        raise HTTPException(status_code=400, detail="Sesión inválida o inactiva")


@app.post("/alumnos/{id}/session/logout")
async def logout(id: int, sessionString: schemas.ValidacionSesion):
    response = table.update_item(
        Key={
            'id': sessionString.sessionString,
            'alumnoId': id
        },
        UpdateExpression="set active = :a",
        ExpressionAttributeValues={
            ':a': False
        },
        ReturnValues="UPDATED_NEW"
    )

    return {"message": "Sesión cerrada"}
