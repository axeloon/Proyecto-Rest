from .db import conectar_bd # Importa la función conectar_bd desde un archivo local

# Función para obtener todas las salas disponibles
def get_rooms():
    conn = conectar_bd() # Conexión a la base de datos

    # Manejo de la conexión a la base de datos
    if conn is not None:
        try:
            cursor = conn.cursor()

            # Consulta para obtener todas las salas
            query = "SELECT * FROM sala;"
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            print("Consulta realizada con éxito")

            return rows # Retorna todas las salas
        except Exception as e:
            print("Error al ejecutar la consulta:", e)
            conn.close()  # En caso de error, cerrar la conexión
            return None # Retorna None en caso de error
    else:
        print("No se pudo conectar a la base de datos")
        return None # Retorna None si no se puede conectar a la base de datos

# Función para obtener una sala específica mediante su código
def fetch_room_by_code(roomCode: str):
    conn = conectar_bd() # Conexión a la base de datos

    # Manejo de la conexión a la base de datos
    if conn is not None:
        try:
            cursor = conn.cursor()

            # Consulta para obtener una sala específica mediante su código
            query = "SELECT * FROM sala WHERE codigo = %s;"
            cursor.execute(query, (roomCode,))
            room = cursor.fetchone()
            cursor.close()
            conn.close()

            if room:
                return room # Retorna la sala encontrada
            else:
                return None # Retorna None si no se encuentra ninguna sala con ese código
        except Exception as e:
            print("Error al ejecutar la consulta:", e)
            conn.close()  # En caso de error, cerrar la conexión
            return None # Retorna None en caso de error
    else:
        print("No se pudo conectar a la base de datos")
        return None  # Retorna None si no se puede conectar a la base de datos