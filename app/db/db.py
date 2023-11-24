import psycopg2

def conectar_bd():
    try:
        conn = psycopg2.connect(
            user="rkqkcsga",
            password="wL1loYaH1PvjfgTmuJUq7r8vKUuFkod_",
            database="rkqkcsga",
            host="isabelle.db.elephantsql.com",
            port=5432  # Puerto por defecto de PostgreSQL
        )
        print("Conexión con la BD establecida con éxito")
        return conn
    except (Exception, psycopg2.Error) as error:
        print("Error al conectar a la base de datos:", error)
        return None  # En caso de error, se devuelve None o se maneja de acuerdo a tus necesidades
