from fastapi import APIRouter, Depends, HTTPException, status  # FastAPI - Enrutamiento, Dependencias, Excepciones HTTP, Códigos de estado
from fastapi.responses import HTMLResponse  # FastAPI - Respuesta HTML

from typing import List, Union  # Typing - Definición de tipos List y Union

from app.auth.google_auth import get_google_credentials, authorize_google_user  # Importaciones relacionadas con la autenticación de Google
from app.auth.jwt import verify_jwt  # Importación para verificar tokens JWT

from app.db.db import conectar_bd  # Conexión a la base de datos
from app.db.reserves import  ReservaSQL, ReservaSearchSQL, reserve_request, fetch_reservations, fetch_room_schedule, cancel_reservation_token  # Operaciones relacionadas con reservas
from app.db.rooms import get_rooms, fetch_room_by_code  # Operaciones relacionadas con salas

from app.resources.recursos import contenido_html, HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR  # Recursos personalizados (HTML, Excepciones HTTP)

router = APIRouter()  # Creación de un enrutador para definir rutas de la API

@router.get("/")  # Ruta raíz de la API
def root():
    return "Hola mundo"  # Retorna un mensaje simple

@router.get("/v1", response_class=HTMLResponse)  # Ruta '/v1' de la API con respuesta HTML
def v1():
    try:
        google_creds = get_google_credentials()  # Obtiene las credenciales de Google
        if google_creds:
            # Verifica la existencia de credenciales válidas y realiza alguna acción (en este caso, podría ser el uso de las credenciales)
            return contenido_html  # Retorna contenido HTML si hay credenciales válidas
        else:
            return "No hay credenciales válidas de Google"  # Mensaje si no hay credenciales válidas
    except Exception as e:
        return f"Error en la autenticación: {str(e)}"  # Mensaje en caso de error durante la autenticación

@router.get("/v1/login")  # Ruta '/v1/login' para la autenticación
def login():
    creds = get_google_credentials()  # Obtiene las credenciales de Google
    if not creds or not creds.valid:  # Verifica la validez de las credenciales
        creds = authorize_google_user()  # Autoriza al usuario en caso de credenciales no válidas o ausentes
    if creds:
        return "Autenticación exitosa", status.HTTP_200_OK  # Retorna mensaje de autenticación exitosa con código 200
    else:
        return "Error en la autenticación", status.HTTP_401_UNAUTHORIZED  # Retorna mensaje de error de autenticación con código 401

@router.get("/v1/rooms/{roomCode}")  # Ruta '/v1/rooms/{roomCode}' para obtener información de una sala por su código
def get_room_by_code(roomCode: str, current_user: dict = Depends(verify_jwt)):  # Parámetro roomCode como parte de la URL y verificación del token JWT
    if current_user:  # Verifica si hay un usuario autenticado
        room_data = fetch_room_by_code(roomCode)  # Obtiene la información de la sala según el código proporcionado
        if room_data:  # Verifica si se encontró información de la sala
            return room_data  # Retorna los datos de la sala
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,  # Retorna error 404 si la sala no se encuentra
                detail=f"Sala con código {roomCode} no encontrada",  # Detalle del error
            )
    else:
        raise HTTP_401_UNAUTHORIZED  # Retorna error 401 si no hay usuario autenticado
    
@router.get("/v1/rooms")  # Ruta '/v1/rooms' para obtener información de las salas
def get_sala(current_user: dict = Depends(verify_jwt)):  # Parámetro current_user para verificar el token JWT
    if current_user:  # Verifica si hay un usuario autenticado
       return get_rooms()  # Retorna la información de las salas si el usuario está autenticado
    else:
        raise HTTP_401_UNAUTHORIZED  # Retorna error 401 si no hay usuario autenticado

@router.post("/v1/reserve/request")  # Ruta '/v1/reserve/request' para solicitar una reserva
async def request(reserve: ReservaSQL, current_user: dict = Depends(verify_jwt)):  # Parámetro reserve para la solicitud de reserva y current_user para verificar el token JWT
    try:
        response = reserve_request(reserve, current_user)  # Realiza la solicitud de reserva
        if response:
            return response  # Retorna la respuesta si la solicitud fue exitosa
        else:
            raise HTTP_500_INTERNAL_SERVER_ERROR  # Retorna error 500 si hubo un error interno del servidor
    except HTTPException as http_exc:
        return http_exc  # Manejo de excepciones HTTP

@router.post("/v1/reserve/search")  # Ruta '/v1/reserve/search' para buscar reservas
def search_reservations(params: ReservaSearchSQL, current_user: dict = Depends(verify_jwt)):  # Parámetro params para la búsqueda y current_user para verificar el token JWT
    if current_user:  # Verifica si hay un usuario autenticado
        reservations = fetch_reservations(params)  # Obtiene las reservas según los parámetros proporcionados
        if reservations:
            return reservations  # Retorna las reservas si se encuentran
        else:
            return {"message": "No se encontraron reservas con los parámetros proporcionados"}  # Retorna mensaje si no se encuentran reservas
    else:
        raise HTTP_401_UNAUTHORIZED  # Retorna error 401 si no hay usuario autenticado

@router.get("/v1/reserve/{roomCode}/schedule/{date}")  # Ruta '/v1/reserve/{roomCode}/schedule/{date}' para obtener el horario de una sala en una fecha específica
def get_room_schedule(roomCode: str, date: str, current_user: dict = Depends(verify_jwt)):  # Parámetros roomCode y date para la sala y fecha respectivamente, current_user para verificar el token JWT
    if current_user:  # Verifica si hay un usuario autenticado
        schedule = fetch_room_schedule(roomCode, date)  # Obtiene el horario de la sala para la fecha proporcionada
        if schedule:
            return schedule  # Retorna el horario de la sala si se encuentra
        else:
            return {"message": "No hay reservas para esta sala en la fecha proporcionada"}  # Retorna mensaje si no hay reservas para la sala y fecha especificadas
    else:
        raise HTTP_401_UNAUTHORIZED  # Retorna error 401 si no hay usuario autenticado

@router.delete("/v1/reserve/{token}/cancel")  # Ruta '/v1/reserve/{token}/cancel' para cancelar una reserva utilizando un token
async def cancel_reservation(token: str, current_user: dict = Depends(verify_jwt)):  # Parámetro token para identificar la reserva a cancelar, current_user para verificar el token JWT
    if current_user:  # Verifica si hay un usuario autenticado
        result = cancel_reservation_token(token)  # Cancela la reserva utilizando el token proporcionado
        if result:
            return result  # Retorna el mensaje de éxito o error desde la función cancel_reservation_token
    else:
        raise HTTP_401_UNAUTHORIZED  # Retorna error 401 si no hay usuario autenticado
