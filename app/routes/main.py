from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse

from pydantic import BaseModel

from datetime import datetime

from app.auth.google_auth import get_google_credentials, authorize_google_user
from app.auth.jwt import verify_jwt
from app.db import conectar_bd

router = APIRouter()

class ReservaSQL(BaseModel):
    usuario: str
    sala: str
    fechainicio: str
    fechatermino: str


# Contenido HTML para una página web simple
contenido_html = f""" 
        <h1>BOOKING UTEM</h1>
        <h2>Para ingresar, registrese con su cuenta utem</h2>
        <button onClick='fetch("http://127.0.0.1:5000/v1/login")'>
                LOGIN
                </button>
        <br></br>
        <button onClick='fetch("http://localhost:5000/v1/protected")'>
                Protected (Solo si tienes token)
                </button>
        <br></br>
        """

@router.get("/")
def root():
    return "hola mundo"

@router.get("/v1", response_class=HTMLResponse)
def v1():
    try:
        google_creds = get_google_credentials()
        if google_creds:
            # Aquí podrías utilizar las credenciales para algo si es necesario
            return contenido_html
        else:
            return "No hay credenciales válidas de Google"
    except Exception as e:
        return f"Error en la autenticación: {str(e)}"

@router.get("/v1/login") #Cambiar a route y probar
def login():
    creds = get_google_credentials()
    if not creds or not creds.valid:
        creds = authorize_google_user()
    if creds:
        return "Autenticación exitosa", status.HTTP_200_OK
    else:
        return "Error en la autenticación", status.HTTP_401_UNAUTHORIZED
    
# Ruta protegida que requiere un token JWT para acceder
@router.get("/v1/protected")
async def protected_route(current_user: dict):
    # Verifica y decodifica el token JWT enviado en la solicitud

    if current_user:
        return {
            "message": "Esta es una ruta protegida",
            "user": current_user["sub"]
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
@router.get("/v1/db")
def get_sala(current_user: dict = Depends(verify_jwt)): #Almacena la información del usuario (mail entre otras cosas)
    conn = conectar_bd()

    if current_user:
        if conn is not None:
            try:
                cursor = conn.cursor()
                query = "SELECT * FROM Sala"
                cursor.execute(query)
                sala = cursor.fetchall()
                cursor.close()
                conn.close()
            except Exception as e:
                print("Error al ejecutar la consulta:", e)
                conn.close()  # En caso de error, cerrar la conexión
                return None
        else:
            print("No se pudo conectar a la base de datos")
            return None
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return sala

@router.get("/v1/email")
def get_email(current_user: dict = Depends(verify_jwt)):
    if current_user:
        return {
            "message": "Este es el mail obtenido del jwt",
            "user": current_user["sub"],
            "email": current_user["email"]
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
@router.post("/v1/reserve/request")
async def request(reserve: ReservaSQL, current_user: dict = Depends(verify_jwt)):
    if current_user:
        conn = conectar_bd()  # Obtiene una conexión a la base de datos
        if conn is not None:
            try:
                cursor = conn.cursor()
                query = "INSERT INTO reserva (usuario, sala, fechainicio, fechatermino) VALUES (%s, %s, %s, %s)"
                values = (reserve.usuario, reserve.sala, reserve.fechainicio, reserve.fechatermino)
                cursor.execute(query, values)
                conn.commit()  # Guarda los cambios en la base de datos
                cursor.close()
                conn.close()  # Cierra la conexión después de su uso
                return {"message": "Reserva creada exitosamente"}
            except Exception as e:
                print("Error al ejecutar la consulta:", e)
                conn.close()  # En caso de error, asegúrate de cerrar la conexión
                return None
        else:
            print("No se pudo conectar a la base de datos")
            return None
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    