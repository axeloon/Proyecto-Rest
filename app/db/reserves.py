from fastapi import HTTPException, status

from pydantic import BaseModel

from .db import conectar_bd
from app.resources.recursos import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST


class ReservaSQL(BaseModel):
    sala: str
    fechainicio: str
    fechatermino: str
    capacidad: int

class ReservaSearchSQL(BaseModel):
    usuario: str = None
    sala: str = None

def reserve_request(reserve: ReservaSQL,current_user: dict):
    conn = conectar_bd()

    if conn is not None:
        try:
            cursor = conn.cursor()

            # Obtener la capacidad de la sala y verificar si está reservada
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
                query_insert = "INSERT INTO reserva (usuario, sala, fechainicio, fechatermino) VALUES (%s, %s, %s, %s);"
                values = (current_user['email'], reserve.sala, reserve.fechainicio, reserve.fechatermino)
                cursor.execute(query_insert, values)
                conn.commit()
                cursor.close()
                conn.close()

                return {"message": "Reserva creada exitosamente"}
        except Exception as e:
            print("Error al ejecutar la consulta:", e)
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al realizar la reserva: {str(e)}"  # Detalle con el mensaje de error
            )
    else:
        print("No se pudo conectar a la base de datos")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al conectar con la base de datos"
        )

def fetch_reservations(params: ReservaSearchSQL):
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
    
def fetch_room_schedule(roomCode: str, date: str):
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
    

def cancel_reservation_token(token: str):
    conn = conectar_bd()

    if conn is not None:
        try:
            cursor = conn.cursor()

            # Verificar si el token de reserva existe en la base de datos
            query_check_token = "SELECT * FROM reserva WHERE token = %s;"
            cursor.execute(query_check_token, (token,))
            reservation = cursor.fetchone()

            if reservation:
                # Si el token existe, anular la reserva eliminando la entrada correspondiente
                query_cancel_reservation = "DELETE FROM reserva WHERE token = %s;"
                cursor.execute(query_cancel_reservation, (token,))
                conn.commit()
                cursor.close()
                conn.close()
                return {"message": "Reserva anulada exitosamente"}
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