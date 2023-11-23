# Importa las clases y módulos necesarios de FastAPI para la creación de la API
from fastapi import HTTPException, status

# Importa las clases y módulos necesarios para la autenticación con Google oauth2
from google.oauth2.credentials import Credentials

# Importa las funciones y la excepción necesarias de la librería 'jose' para trabajar con JSON Web Tokens (JWT)
from jose import jwt, JWTError

# Importa clases que son utilizadas para trabajar con fechas y duraciones en Python.
from datetime import datetime, timedelta

from .peopleAPI import get_google_email #Obtiene el email de las credenciales de google

# Lista de ámbitos (scopes) para la autenticación con Google OAuth2
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']
PASSWD = '123456' #Contraseña para firmar el JWT
ALGORITHM = "HS256" # Algoritmo utilizado para la codificación y decodificación del token JWT

jwtToken = None

# Función para crear y codificar un token JWT a partir de las credenciales de Google
def createJWT(google_token: Credentials):
    global jwtToken

    email = get_google_email(google_token)

    # Configura el payload del token JWT con información relevante
    payload = {
        "sub": google_token.token,
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "scopes": SCOPES,
        #Se puede ingresar más información si es necesario
    }
    # Codifica el token JWT usando la contraseña (PASSWD) y el algoritmo (ALGORITHM)
    jwtToken = jwt.encode(payload, key=PASSWD, algorithm=ALGORITHM)

# Función para verificar y decodificar un token JWT
def verify_jwt():
    global jwtToken #Referencia global
    # Excepción para manejar el caso en que el token no está disponible
    if jwtToken is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no disponible",
            headers={"WWW-Authenticate": "Bearer"}
        )
    try:
        payload = jwt.decode(jwtToken, key=PASSWD, algorithms=[ALGORITHM])
        return payload # Retorna el payload del token JWT decodificado
    # Excepción para manejar errores al decodificar el token
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error al decodificar el token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    

