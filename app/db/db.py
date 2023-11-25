import psycopg2
import json

def cargar_credenciales():
    try:
        with open('config.json') as config_file:
            config = json.load(config_file)
        return config.get('DB_CONFIG')
    except FileNotFoundError as e:
        print(f"El archivo 'credenciales.json' no se encontró: {e}")
        return None

def conectar_bd():
    db_config = cargar_credenciales()
    if db_config:
        try:
            conn = psycopg2.connect(**db_config)
            print("Conexión con la BD establecida con éxito")
            return conn
        except (Exception, psycopg2.Error) as error:
            print("Error al conectar a la base de datos:", error)
            return None
    else:
        return None