from fastapi import HTTPException, status

from pydantic import BaseModel

from .db import conectar_bd # Importa la función conectar_bd desde un archivo local
from app.resources.recursos import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST

from typing import Optional


# Definición de modelos Pydantic para la validación de datos en las peticiones
class ReservaSQL(BaseModel):
    sala: str
    fechainicio: str
    fechatermino: str
    capacidad: int

class ReservaSearchSQL(BaseModel):
    usuario: str = None
    sala: str = None

class Booking(BaseModel):
    token: str
    userEmail: str
    roomCode: str
    start: str
    end: str

# Función para realizar una solicitud de reserva

def reserve_request(reserve: ReservaSQL, current_user: dict) -> Optional[dict]:
    conn = conectar_bd()

    if conn is not None:
        try:
            cursor = conn.cursor()

            # Verificar disponibilidad de la sala
            query_info = "SELECT capacidad, reservado FROM sala WHERE codigo = %s;"
            cursor.execute(query_info, (reserve.sala,))
            result = cursor.fetchone()
            capacity, is_reserved = result[0], result[1]

            if is_reserved:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede realizar la reserva porque la sala está reservada"
                )
            
            if capacity < reserve.capacidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede realizar la reserva debido a la capacidad máxima de la sala"
                )
            else:
                # Realizar la reserva
                query_insert = "INSERT INTO reserva (usuario, sala, fechainicio, fechatermino) VALUES (%s, %s, %s, %s) RETURNING *;"
                values = (current_user['email'], reserve.sala, reserve.fechainicio, reserve.fechatermino)
                cursor.execute(query_insert, values)
                conn.commit()

                # Obtener los detalles de la reserva recién creada
                reservation_details = cursor.fetchone()
                cursor.close()
                conn.close()

                # Formatear los resultados en un diccionario
                reservation_info = {
                    "token": reservation_details[0],
                    "usuario": reservation_details[1],
                    "sala": reservation_details[2],
                    "fechainicio": str(reservation_details[3]),
                    "fechatermino": str(reservation_details[4])
                    # Agrega más campos según tu estructura de la tabla 'reserva'
                }

                return reservation_info
        except Exception as e:
            print("Error al ejecutar la consulta:", e)
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al realizar la reserva: {str(e)}"
            )
    else:
        print("No se pudo conectar a la base de datos")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al conectar con la base de datos"
        )


# Función para obtener reservas según criterios de búsqueda
def fetch_reservations(params: ReservaSearchSQL):
     # Lógica similar a la anterior para manejar las reservas según los parámetros de búsqueda
    conn = conectar_bd()

    if conn is not None:
        try:
            cursor = conn.cursor()
            if params.sala and params.usuario:
                query = "SELECT * FROM reserva WHERE usuario = %s AND sala = %s;"
                cursor.execute(query, (params.usuario, params.sala))
            elif params.usuario:
                query = "SELECT * FROM reserva WHERE usuario = %s;"
                cursor.execute(query, (params.usuario,))
            else:
                return {"message": "Se requiere al menos el campo 'usuario' para la búsqueda."}

            reservations = cursor.fetchall()
            cursor.close()
            conn.close()

            if reservations:
                return reservations
            else:
                return None
        except Exception as e:
            print("Error al ejecutar la consulta:", e)
            conn.close()  # En caso de error, cerrar la conexión
            return None
    else:
        print("No se pudo conectar a la base de datos")
        return None

# Función para obtener el horario de una sala en una fecha específica
def fetch_room_schedule(roomCode: str, date: str):
    # Lógica similar a las anteriores para obtener el horario de una sala en una fecha específica
    conn = conectar_bd()

    if conn is not None:
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM reserva WHERE sala = %s AND DATE(fechainicio) = %s;"
            cursor.execute(query, (roomCode, date))
            
            schedule = cursor.fetchall()
            cursor.close()
            conn.close()

            if schedule:
                return schedule
            else:
                return None
        except Exception as e:
            print("Error al ejecutar la consulta:", e)
            conn.close()  # En caso de error, cerrar la conexión
            return None
    else:
        print("No se pudo conectar a la base de datos")
        return None
    
# Función para cancelar una reserva utilizando un token
def cancel_reservation_token(token: str) -> Optional[dict]:
    conn = conectar_bd()

    if conn is not None:
        try:
            cursor = conn.cursor()

            # Verificar si el token de reserva existe en la base de datos
            query_check_token = "SELECT * FROM reserva WHERE token = %s;"
            cursor.execute(query_check_token, (token,))
            reservation = cursor.fetchone()

            if reservation:
                # Guardar la información de la reserva antes de eliminarla
                reservation_info = {
                    "token": reservation[0],
                    "usuario": reservation[1],
                    "sala": reservation[2],
                    "fechainicio": str(reservation[3]),
                    "fechatermino": str(reservation[4]),
                    # Agregar más campos según la estructura de tu tabla 'reserva'
                }

                # Anular la reserva eliminando la entrada correspondiente
                query_cancel_reservation = "DELETE FROM reserva WHERE token = %s;"
                cursor.execute(query_cancel_reservation, (token,))
                conn.commit()
                cursor.close()
                conn.close()

                # Devolver la información de la reserva eliminada
                return reservation_info
            else:
                # Si el token no existe, retornar un mensaje de error
                raise HTTPException(
                    status_code=404,
                    detail="El token de reserva no existe"
                )
        except Exception as e:
            print("Error al ejecutar la consulta:", e)
            conn.close()
            raise HTTPException(
                status_code=500,
                detail=f"Error al anular la reserva: {str(e)}"
            )
    else:
        raise HTTPException(
            status_code=500,
            detail="Error al conectar con la base de datos"
        )