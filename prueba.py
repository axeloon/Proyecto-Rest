from __future__ import print_function

import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import jwt


#Salto de linea (se puede optimizar)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']

app = FastAPI()

passwd = '123456' #Contraseña para firmar el JWT

br = f"""
<br></br>
"""

@app.get("/", response_class=HTMLResponse)
def root():
    contenido_html = f""" 
        <h1>BOOKING UTEM</h1>
        <h2>Para ingresar, registrese con su cuenta utem</h2>
        <button onClick='fetch("http://127.0.0.1:5000/v1/login")'>
                LOGIN
                </button>
        <br></br>
        """
    if os.path.exists('token.json') and os.path.exists('jwtToken.jwt'):
        with open('token.json', 'r') as archivo:
            token = json.load(archivo)
        with open('jwtToken.jwt', 'r') as archivo:
            jwt = archivo.read()

        token = token["token"]
        return(contenido_html + "Token: " + token + br + "JWT: " + jwt)
    
    else:
        return (contenido_html)


# algo así deberia ir


@app.get("/v1/login")
def login():
    HTMLResponse('''<h3> ERROR, TOKEN NO CREADO </h3>''')
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return "token creado"


@app.get("/v1/token")
def token():
    if os.path.exists('token.json'):
        with open('token.json', 'r') as archivo:
            datos = json.load(archivo)
    else:
        return ('No existe token')
    
    return ("Token: " + datos["token"])

@app.get("/v1/jwt")
def jwtToken():
    if os.path.exists('token.json'):
        with open('token.json', 'r') as archivo:
            datos = json.load(archivo)
            #token = datos["token"]
            jwtToken = jwt.encode(datos, passwd, algorithm='HS256')
    with open('jwtToken.jwt', "w") as archivo:  #Guarda el JWT en la carpeta
        archivo.write(jwtToken)

    return ("JWT: " + jwtToken)


if __name__ == '__main__':
    main()
        
