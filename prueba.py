# Importa el módulo 'os.path' para realizar operaciones relacionadas con rutas y archivos en el sistema operativo
import os.path

# Importa las clases y módulos necesarios para la autenticación con Google oauth2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Importa las clases y módulos necesarios de FastAPI para la creación de la API
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse

# Importa las funciones y la excepción necesarias de la librería 'jose' para trabajar con JSON Web Tokens (JWT)
from jose import jwt, JWTError

# Importa clases que son utilizadas para trabajar con fechas y duraciones en Python.
from datetime import datetime, timedelta

# Lista de ámbitos (scopes) para la autenticación con Google OAuth2
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']
PASSWD = '123456' #Contraseña para firmar el JWT
ALGORITHM = "HS256" # Algoritmo utilizado para la codificación y decodificación del token JWT

# Crea una instancia de la clase FastAPI para construir la aplicación web
app = FastAPI()
# Variable global para almacenar el token JWT, inicializada como None
jwtToken = None

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

# Función para verificar y decodificar un token JWT
def verify_jwt():
    global jwtToken     # Se llama a la variable global jwtToken
    decode = jwtToken   # Se crea una copia de la variable global para utilizarla

    # Excepción para manejar el caso en que el token no está disponible
    credentialExeption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token no disponible",
        headers={"WWW-Authenticate": "Bearer"}
    )
    # Excepción para manejar errores al decodificar el token
    decodeExeption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Error al decodificar el token",
        headers={"WWW-Authenticate": "Bearer"}
    )
    # Verifica si el token no está disponible y lanza la excepción correspondiente
    if jwtToken is None:
        raise credentialExeption
    # Intenta decodificar el token y retorna el payload si tiene éxito
    try:
        payload = jwt.decode(decode, key=PASSWD, algorithms=[ALGORITHM])
        return payload  # Retorna el payload del token JWT decodificado
    # Lanza una excepción si hay un error al decodificar el token
    except JWTError:
        raise decodeExeption
    

# Función para crear un token JWT a partir de las credenciales de Google
def createJWT(google_token: Credentials):

    # Configura el payload del token JWT con información relevante
    payload = {
        "sub": google_token.token,
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "scopes": SCOPES,
        #Se puede ingresar más información si es necesario
    }
    # Codifica el token JWT usando la contraseña (PASSWD) y el algoritmo (ALGORITHM)
    jwtoken = jwt.encode(payload, key=PASSWD, algorithm=ALGORITHM)
    return jwtoken  # Retorna el token JWT recién creado

    
# Ruta principal de la aplicación que devuelve contenido HTML
@app.get("/", response_class=HTMLResponse)
def root():
    # Verifica si existe el archivo 'token.json'
    if os.path.exists('token.json'):
        # Carga las credenciales desde el archivo 'token.json' y crea el JWT
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        createJWT(creds) #Crea el JWT con las credenciales de Google
        return(contenido_html + "Token ya creado")
    # Si no existe el archivo 'token.json', simplemente devuelve el contenido HTML
    return (contenido_html)

# Ruta para el proceso de inicio de sesión y generación del token JWT
@app.get("/v1/login")
def login():
    global jwtToken
    creds = None
    
    # Verifica si existe el archivo 'token.json' y carga las credenciales
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        jwtToken = createJWT(creds) #Crea el JWT con las credenciales de google
    # Si no hay credenciales válidas, inicia el flujo de autorización
    if not creds or not creds.valid:
        # Si las credenciales existen pero están vencidas, realiza una actualización
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Si no hay credenciales, inicia el flujo de autorización desde el archivo 'credentials.json'
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
          
        # Guarda las credenciales en el archivo 'token.json'
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            jwtToken = createJWT(creds) #Crea el JWT con las credenciales de google
    return jwtToken     # Retorna el token JWT generado  


# Ruta protegida que requiere un token JWT para acceder
@app.get("/v1/protected")   #Primero hay que pasar por el login, para que el token se genere, luego, al acceder a esta ruta se decodifica
def protected_route(current_user: dict = Depends(verify_jwt)):  # Verifica y decodifica el token JWT enviado en la solicitud
    # Retorna un diccionario con un mensaje y la información del usuario para la ruta protegida
    return {
        "message": "Esta es una ruta protegida",
        "user": current_user["sub"]
    }