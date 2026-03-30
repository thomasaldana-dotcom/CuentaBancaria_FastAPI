from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


#Tabla usuarios
class UsuarioDb(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    apellido = Column(String)
    correo = Column(String, unique=True, index=True)
    contrasenia_encriptada = Column(String)
    saldo = Column(Float, default = 0.0)
    numero_cuenta = Column(String, unique=True, index=True)
    transacciones = relationship("TransaccionDb", back_populates="dueño")

class TransaccionDb(Base):
    __tablename__ = "transacciones"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String)
    monto = Column(Float)
    fecha = Column(DateTime, default=datetime.utcnow)
    cuenta_destino = Column(String, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))

    dueño = relationship("UsuarioDb", back_populates="transacciones")

