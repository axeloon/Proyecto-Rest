import json

# Importa las clases y módulos necesarios de FastAPI para la creación de la API
from fastapi import HTTPException, status

# Importa las clases y módulos necesarios para la autenticación con Google oauth2
from google.oauth2.credentials import Credentials

# Importa las funciones y la excepción necesarias de la librería 'jose' para trabajar con JSON Web Tokens (JWT)
from jose import jwt, JWTError

# Importa clases que son utilizadas para trabajar con fechas y duraciones en Python.
from datetime import datetime, timedelta

from .peopleAPI import get_google_email # Obtiene el email de las credenciales de Google

#Carga la configuración desde un archivo JSON
def load_config():
    with open('config.json') as config_file:
        config = json.load(config_file)  # Lee y convierte el archivo JSON a un diccionario Python
    return config

config = load_config()  # Carga la configuración del archivo JSON

# Lista de ámbitos (scopes) para la autenticación con Google OAuth2
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']

PASSWD = config.get('PASSWD')  # Obtiene la contraseña para firmar el JWT desde la configuración
ALGORITHM = config.get('ALGORITHM')  # Obtiene el algoritmo usado para la codificación/decodificación del token JWT

jwtToken = None  # Variable global para almacenar el token JWT

#Crea y codifica un token JWT a partir de las credenciales de Google
def createJWT(google_token: Credentials):
    global jwtToken

    email = get_google_email(google_token)  # Obtiene el email asociado a las credenciales de Google

    # Configura el payload del token JWT con información relevante
    payload = {
        "sub": google_token.token,  # Identificador único del token de Google
        "email": email,  # Email obtenido desde las credenciales de Google
        "exp": datetime.utcnow() + timedelta(minutes=15),  # Tiempo de expiración del token (15 minutos desde ahora)
        "scopes": SCOPES,  # Lista de ámbitos para la autenticación
        # Se puede ingresar más información si es necesario
    }

    # Codifica el token JWT usando la contraseña (PASSWD) y el algoritmo (ALGORITHM)
    jwtToken = jwt.encode(payload, key=PASSWD, algorithm=ALGORITHM)

#Verifica y decodifica un token JWT
def verify_jwt():
    global jwtToken  # Referencia global

    # Excepción para manejar el caso en que el token no está disponible
    if jwtToken is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no disponible",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        # Decodifica el token JWT usando la contraseña (PASSWD) y el algoritmo (ALGORITHM)
        payload = jwt.decode(jwtToken, key=PASSWD, algorithms=[ALGORITHM])
        return payload  # Retorna el payload del token JWT decodificado

    # Excepción para manejar errores al decodificar el token
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error al decodificar el token",
            headers={"WWW-Authenticate": "Bearer"}
        )
