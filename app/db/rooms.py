from .db import conectar_bd

def get_rooms():
    conn = conectar_bd()

    if conn is not None:
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM sala;"
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            print("Consulta realizada con éxito")

            return rows
        except Exception as e:
            print("Error al ejecutar la consulta:", e)
            conn.close()  # En caso de error, cerrar la conexión
            return None
    else:
        print("No se pudo conectar a la base de datos")
        return None

def fetch_room_by_code(roomCode: str):
    conn = conectar_bd()

    if conn is not None:
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM sala WHERE codigo = %s;"
            cursor.execute(query, (roomCode,))
            room = cursor.fetchone()
            cursor.close()
            conn.close()

            if room:
                return room
            else:
                return None
        except Exception as e:
            print("Error al ejecutar la consulta:", e)
            conn.close()  # En caso de error, cerrar la conexión
            return None
    else:
        print("No se pudo conectar a la base de datos")
        return None