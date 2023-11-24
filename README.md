# Proyecto-Rest
Este repositorio contiene una implementación de autenticación a través de Google Oauth2, utilizando JWT.
Proyecto API REST en FastAPI para la asignatura Computación Paralela 2-2023

 ## Características:
 - Módulos google.oauth2.credentials para la autenticación com Google Oauth2.
 - Generación de token JWT con algoritmo de firma HS256.
   
 ## Requirementos:
- Python3.6+

## Como ejecutar el script:
- Para ejecución local
1. Clonar este repositorio en la máquina local
2. Navegar al directorio del proyecto a través de una terminal
3. Crear un entorno virtual (virtualenv) `python -m venv .venv` Windows por defecto o `python3 -m venv .venv`
4. Activar el entorno virtual (virtualenv) 
 `.venv\Scripts\activate (Windows)` `.venv/bin/activate (Unix)`
5. Instala los requerimientos 
    `python -m pip install -r requirements.txt`
6. Crear un archivo llamado `credentials.json` que contenga las credenciales:
    - El archivo debería tener el siguiente formato: 
    `{"installed":{"client_id":" ","project_id":" ","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":" ","redirect_uris":["http://localhost"]}}`
    - Llenar los espacios en blanco con tus credenciales o bien, arrastra tu archivo JSON
    - Crear un archivo llamado `config.json` que contenga la contraseña y el algoritmo para firmar los JWT:
    - El archivo debería tener el siguiente formato:
    `{"PASSWD": "123456","ALGORITHM": "HS256"}`
7. Para correr la App:
    - Abrir una terminal en la carpeta raíz del proyecto
    - Con el entorno virtual (venv) activado, ejecutar: 
    `uvicorn main:app --port 5000 --reload`
    - En la dirección `localhost:5000` se encontrará la API Rest
8. Documentación de la API (Swagger)
    -En un navegador, acceder a la dirección:
    `localhost:5000/docs` 
    Para acceder a la documentación y realizar pruebas a la API
