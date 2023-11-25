# Importa el módulo 'os.path' para realizar operaciones relacionadas con rutas y archivos en el sistema operativo
import os.path

from fastapi import Response

# Importa las clases y módulos necesarios para la autenticación con Google oauth2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build  # Importa la función build para crear un servicio

from .jwt import createJWT  # Importa la función createJWT desde un archivo local llamado jwt

# Lista de ámbitos (scopes) para la autenticación con Google OAuth2
SCOPES = [
    'openid',  # Para autenticación abierta
    'https://www.googleapis.com/auth/userinfo.email',  # Acceso al email del usuario
    'https://www.googleapis.com/auth/userinfo.profile'  # Acceso al perfil del usuario
]

#Obtiene las credenciales de Google desde un archivo local 'token.json' si existe
def get_google_credentials():
    if os.path.exists('token.json'):  # Verifica si el archivo 'token.json' existe en el sistema
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)  # Carga las credenciales desde el archivo 'token.json' usando los ámbitos especificados
        createJWT(creds)  # Crea un token JWT utilizando las credenciales obtenidas
        return creds  # Retorna las credenciales cargadas desde el archivo 'token.json'
    return None  # Retorna None si el archivo 'token.json' no existe


# Actualizando la función get_login para devolver la URL de autorización como una redirección
def get_login():
    redirect_uri = "https://159.223.193.199.nip.io:9806/v1/callback"
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, redirect_uri=redirect_uri)
    auth_url, _ = flow.authorization_url(prompt='consent')
    return Response(content=auth_url, status_code=307)  # Devolver la URL como una respuesta de redirección

def callback_google(code: str):
    redirect_uri = "https://159.223.193.199.nip.io:9806/v1/callback"  # Reemplaza esto con tu URI de redirección registrada en Google Cloud
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, redirect_uri=redirect_uri)
    flow.fetch_token(code=code)

    creds = flow.credentials

    with open('token.json', 'w') as token:
        token.write(creds.to_json())
        createJWT(creds)  # Crea un token JWT utilizando las credenciales obtenidas


    return {"message": "Credenciales de Google almacenadas correctamente"}

