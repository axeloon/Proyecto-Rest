from googleapiclient.discovery import build  # Importa la función build para crear un servicio
from google.oauth2.credentials import Credentials

def get_google_email(creds: Credentials):
    try:
        # Crea un servicio para la API de People con las credenciales autorizadas
        service = build('people', 'v1', credentials=creds)

        # Llama al método de la API de People para obtener la información del usuario
        # Este ejemplo supone que ya tienes permisos para acceder al perfil básico del usuario
        user_info = service.people().get(resourceName='people/me', personFields='emailAddresses').execute()

        # Obtiene el correo electrónico del usuario desde la respuesta
        email = user_info['emailAddresses'][0]['value']

        # Imprime o almacena el correo electrónico para su uso posterior en tu base de datos u otras operaciones
        print(f"Correo electrónico del usuario: {email}")
    except Exception as e:
        print(f'Error al obtener el correo electrónico: {e}')
    
    return email