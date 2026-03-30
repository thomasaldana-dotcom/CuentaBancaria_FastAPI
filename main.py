from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import engine
from routers import auth, transacciones

#models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Banco Thom",
    description="Api opara gestionar cuentas bancarias de los usuarios",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(transacciones.router)

@app.get("/")
def bienvenida():
    return {
        "mensaje": "Funcionando correctamente"
    }