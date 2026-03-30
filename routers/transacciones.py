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


@router.post("/transferir", response_model=schemas.TransaccionResponse)
def transferir_plata(transaccion: schemas.TransaccionCreate, db: Session = Depends(get_db), usuario_actual: models.UsuarioDb = Depends(obtener_usuario_actual)):
    
    if transaccion.monto <= 0:
        raise HTTPException(status_code=400, detail="El monto a transferir debe ser mayor a 0.")
        
    if not transaccion.cuenta_destino:
        raise HTTPException(status_code=400, detail="Debe indicar el número de cuenta destino, perro. ¿A quién le giramos?")
        
    if transaccion.cuenta_destino == usuario_actual.numero_cuenta:
        raise HTTPException(status_code=400, detail="No puede transferirse plata a usted mismo, no sea loco.")
        
    if transaccion.monto > usuario_actual.saldo:
        raise HTTPException(status_code=400, detail="¡Fondos insuficientes para esta transferencia!")

    usuario_destino = db.query(models.UsuarioDb).filter(models.UsuarioDb.numero_cuenta == transaccion.cuenta_destino).first()
    
    if not usuario_destino:
        raise HTTPException(status_code=404, detail="Paila, esa cuenta destino no existe en nuestro banco.")

    usuario_actual.saldo -= transaccion.monto
    usuario_destino.saldo += transaccion.monto

    nuevo_recibo = models.TransaccionDb(
        usuario_id=usuario_actual.id,
        tipo="TRANSFERENCIA",
        monto=transaccion.monto,
        cuenta_destino=transaccion.cuenta_destino
    )

    db.add(nuevo_recibo)
    db.commit()
    db.refresh(nuevo_recibo)

    return nuevo_recibo