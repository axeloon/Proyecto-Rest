from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse

from app.auth.google_auth import get_google_credentials, authorize_google_user
from app.auth.jwt import verify_jwt
from app.db import conectar_bd

router = APIRouter()


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
    google_creds = get_google_credentials()
    if google_creds:
        # Aquí podrías utilizar las credenciales para algo si es necesario
        return contenido_html
    else:
        return "No hay credenciales válidas de Google"

@router.get("/v1/login")
def login():
    creds = get_google_credentials()
    if not creds or not creds.valid:
        creds = authorize_google_user()
    if creds:
        return "Autenticación exitosa"
    else:
        return "Error en la autenticación"
    
# Ruta protegida que requiere un token JWT para acceder
@router.get("/v1/protected")
async def protected_route(current_user: dict = Depends(verify_jwt)):
    # Verifica y decodifica el token JWT enviado en la solicitud
    # Dependiendo de tu implementación de autenticación, aquí podrías realizar acciones
    # utilizando la información del usuario (extraída del token) si el token es válido.
    # Por ejemplo, podrías realizar operaciones específicas del usuario autenticado.

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
async def get_sala(current_user: dict = Depends(verify_jwt)): #Almacena la información del usuario (mail entre otras cosas)
    conn = conectar_bd()  # No se usa 'await' ya que conectar_bd() no es una función asíncrona

    if current_user:
        if conn is not None:
            try:
                cursor = conn.cursor()
                query = "SELECT * FROM Sala"
                cursor.execute(query)
                sala = cursor.fetchall()
                cursor.close()
                conn.close()
                return sala
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
        
