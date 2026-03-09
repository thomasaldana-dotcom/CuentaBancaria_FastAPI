from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

#Login ....
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer # Se encarga de revisar automaticamente si el forntend mando el token en las cabeceras de las peticiones web 
from datetime import datetime, timedelta
from jose import jwt, JWTError 

import random
from database import get_db
import models, schemas

router = APIRouter(
    prefix="/auth",
    tags=["Autenticacion"]
)

#Router es para hacer todas las acciones de auth en un pasillo aparte y no mezclarlo con otras acciones

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #Licuadora de contraseñas

#Login
SECRET_KEY = "tu_clave_secreta_super_segura" 
ALGORITHM = "HS256" #Crear la firma mezclada mediante hs256 estandar de la indsutria
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def crear_token(data: dict): #Funcion para crear el token al usuario
    codificar = data.copy() #Copia de los datos
    expiracion = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) #Tiempo de expiracion del token
    codificar.update({"exp": expiracion}) #Actualiza la expiracion

    token_jwt = jwt.encode(codificar, SECRET_KEY, algorithm=ALGORITHM) #Crea el token
    return token_jwt

@router.post("/login", response_model=schemas.Token) #Revisa los datos humanos para dejar entrar a la persona y darle un token
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
    



#Escaner de tokens (Seguridad)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def obtener_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)): # Revisa el token y datos detras de la maquina es decir ya no importa la contraseña ni el correo
    exepcion_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales invalidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario: str = payload.get("sub")
        if id_usuario is None:
            raise exepcion_credenciales
    except JWTError:
        raise exepcion_credenciales
    
    usuario = db.query(models.UsuarioDb).filter(models.UsuarioDb.id == id_usuario).first()
    if usuario is None:
        raise exepcion_credenciales
    return usuario


#Ruta protegida para ver el perfil y el saldo
@router.get("/perfil", response_model=schemas.UsuarioResponse)
def leer_perfil(usuario_actual: models.UsuarioDb = Depends(obtener_usuario_actual)):
    return usuario_actual