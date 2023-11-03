# Proyecto-Rest
 Proyecto API REST en FastAPI para el ramo computación paralela 2-2023

 ## Requirementoss:
- Python3.6+

## Como correr el script:
- Crear un entorno virtual (virtualenv) `python3 -m venv .venv`
- Activar el entorno virtual (virtualenv) `. .venv/Scripts/activate (Windows)` `. .venv/bin/activate (Unix)`
- Instala los requerimientos `python -m pip install -r requirements.txt`
- Crear un archivo llamado `credentials.json` que contenga las credenciales:
    - El archivo debería tener el siguiente formato: `{"installed":{"client_id":" ","project_id":" ","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":" ","redirect_uris":["http://localhost"]}}`
    - Llenar los espacios en blanco con tus credenciales o bien, arrastra tu archivo JSON
- Para correr la App:
    - Abrir una terminal en la carpeta raíz del proyecto
    - Con el entorno virtual (venv) activado, ejecutar: `uvicorn prueba:app --port 5000 --reload`
    - En la dirección `localhost:5000` estará la API Rest
