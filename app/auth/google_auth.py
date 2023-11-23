# Importa el módulo 'os.path' para realizar operaciones relacionadas con rutas y archivos en el sistema operativo
import os.path

# Importa las clases y módulos necesarios para la autenticación con Google oauth2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from .jwt import createJWT, jwtToken

# Lista de ámbitos (scopes) para la autenticación con Google OAuth2
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']

def get_google_credentials():
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        createJWT(creds)
        return creds
    return None

""" def refresh_google_credentials(creds):
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        return creds
    return None """

def authorize_google_user():
    creds = None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        createJWT(creds)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
        createJWT(creds)
    return creds