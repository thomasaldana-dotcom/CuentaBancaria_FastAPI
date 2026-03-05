from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import List, Optional
from datetime import datetime

class TransaccionBase(BaseModel):
    monto: float = Field(gt=0, description="Monto debe ser mayor a 0")

class TransaccionCreate(TransaccionBase):
    tipo: str
    numero_cuenta_destino: Optional[str] = None

    @model_validator(mode="after")
    def validar_transaccion(self):
        if self.tipo == "transferencia" and not self.numero_cuenta_destino:
            raise ValueError("Debe especificar una cuenta de destino para transferencias")
        return self

class TransaccionResponse(TransaccionBase):
    id: int
    tipo: str
    fecha: datetime
    usuario_id: int
    cuenta_destino: Optional[str] = None

    class Config:
        from_attributes = True


class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    correo: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioResponse(UsuarioBase):
    id: int
    saldo: float
    numero_cuenta: str
    transacciones: List[TransaccionResponse] = []

    class Config:
        from_attributes = True



#Token - Login

class Token(BaseModel):
    access_token: str
    token_type: str




