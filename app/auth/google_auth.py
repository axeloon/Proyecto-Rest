# Importa el módulo 'os.path' para realizar operaciones relacionadas con rutas y archivos en el sistema operativo
import os.path

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

#Autoriza al usuario con Google y guarda las credenciales en 'token.json
def authorize_google_user():
    creds = None  # Inicializa las credenciales como None
    if creds != None and creds.expired and creds.refresh_token:
        creds.refresh(Request())  # Refresca las credenciales si están expiradas y se puede realizar un refresh
        createJWT(creds)  # Crea un token JWT utilizando las credenciales actualizadas
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)  # Crea un flujo de autorización desde el archivo 'credentials.json' utilizando los ámbitos especificados
        creds = flow.run_local_server(port=0)  # Ejecuta un servidor local para realizar la autorización
    with open('token.json', 'w') as token:
        token.write(creds.to_json())  # Escribe las credenciales en formato JSON en el archivo 'token.json'
        createJWT(creds)  # Crea un token JWT utilizando las credenciales obtenidas
    return creds  # Retorna las credenciales autorizadas y guardadas en 'token.json'
