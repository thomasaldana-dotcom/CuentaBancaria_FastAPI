from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

import models, schemas
from routers.auth import obtener_usuario_actual

router = APIRouter(
    prefix="/transacciones",
    tags=["Transacciones"]
)

@router.post("/depositar", response_model=schemas.TransaccionResponse)
def depositar_dinero(transaccion: schemas.TransaccionCreate, db: Session = Depends(get_db), usuario_actual: models.UsuarioDb = Depends(obtener_usuario_actual)):

    if transaccion.monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")
    
    usuario_actual.saldo += transaccion.monto

    nuevo_recibo = models.TransaccionDb(
        usuario_id=usuario_actual.id,
        tipo="DEPOSITO",
        monto=transaccion.monto
    )

    db.add(nuevo_recibo)
    db.commit()
    db.refresh(nuevo_recibo)

    return nuevo_recibo


@router.post("/retirar", response_model=schemas.TransaccionResponse)
def retirar_plata(transaccion: schemas.TransaccionCreate, db: Session = Depends(get_db), usuario_actual: models.UsuarioDb = Depends(obtener_usuario_actual)):
    
    if transaccion.monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0.")
        
    if transaccion.monto > usuario_actual.saldo:
        raise HTTPException(status_code=400, detail="¡Fondos insuficientes, vaciado! Vaya trabaje.")

    usuario_actual.saldo -= transaccion.monto

    nuevo_recibo = models.TransaccionDb(
        usuario_id=usuario_actual.id,
        tipo="RETIRO",
        monto=transaccion.monto
    )

    db.add(nuevo_recibo)
    db.commit()
    db.refresh(nuevo_recibo)

    return nuevo_recibo
    