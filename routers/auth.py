from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

#Login ....
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt, JWTError 

import random
from database import get_db
import models, schemas

router = APIRouter(
    prefix="/auth",
    tags=["Autenticacion"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Login
SECRET_KEY = "tu_clave_secreta_super_segura" 
ALGORITHM = "HS256" #Crear la firma mezclada mediante hs256 estandar de la indsutria
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def crear_token(data: dict):
    codificar = data.copy()
    expiracion = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    codificar.update({"exp": expiracion})

    token_jwt = jwt.encode(codificar, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

@router.post("/login", response_model=schemas.Token)
def login(credenciales: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(models.UsuarioDb).filter(models.UsuarioDb.correo == credenciales.username).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    contrasenia_correcta = pwd_context.verify(credenciales.password, usuario.contrasenia_encriptada)
    
    if not contrasenia_correcta:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    token = crear_token({"sub": str(usuario.id)})
    
    return {"access_token": token, 
            "token_type": "bearer"
    }
    
    
    

def generar_numero_cuenta():
    return str(random.randint(1000000000, 9999999999))

@router.post("/registro", response_model=schemas.UsuarioResponse)
def registrar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existe = db.query(models.UsuarioDb).filter(models.UsuarioDb.correo == usuario.correo).first()
    if usuario_existe:
        raise HTTPException(status_code=400, detail="El correo ya esta registrado")
    
    numero_cuenta = generar_numero_cuenta()

    while db.query(models.UsuarioDb).filter(models.UsuarioDb.numero_cuenta == numero_cuenta).first():
        numero_cuenta = generar_numero_cuenta()
    
    hashed_password = pwd_context.hash(usuario.password)

    nuevo_usuario = models.UsuarioDb(
        nombre = usuario.nombre,
        apellido = usuario.apellido,
        correo = usuario.correo,
        contrasenia_encriptada = hashed_password,
        numero_cuenta = numero_cuenta

    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario
    
#Este es un comentario de prueba para hacer un commit en git 
    

