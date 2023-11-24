from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse

from typing import List, Union

from app.auth.google_auth import get_google_credentials, authorize_google_user
from app.auth.jwt import verify_jwt

from app.db.db import conectar_bd
from app.db.reserves import  ReservaSQL, ReservaSearchSQL, reserve_request, fetch_reservations, fetch_room_schedule, cancel_reservation_token 
from app.db.rooms import get_rooms, fetch_room_by_code

from app.resources.recursos import contenido_html, HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR



router = APIRouter()

@router.get("/")
def root():
    return "hola mundo"

@router.get("/v1", response_class=HTMLResponse)
def v1():
    try:
        google_creds = get_google_credentials()
        if google_creds:
            # Aquí podrías utilizar las credenciales para algo si es necesario
            return contenido_html
        else:
            return "No hay credenciales válidas de Google"
    except Exception as e:
        return f"Error en la autenticación: {str(e)}"

@router.get("/v1/login") #Cambiar a route y probar
def login():
    creds = get_google_credentials()
    if not creds or not creds.valid:
        creds = authorize_google_user()
    if creds:
        return "Autenticación exitosa", status.HTTP_200_OK
    else:
        return "Error en la autenticación", status.HTTP_401_UNAUTHORIZED

@router.get("/v1/rooms/{roomCode}")
def get_room_by_code(roomCode: str, current_user: dict = Depends(verify_jwt)):
    if current_user:
        room_data = fetch_room_by_code(roomCode)
        if room_data:
            return room_data
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sala con código {roomCode} no encontrada",
            )
    else:
        raise HTTP_401_UNAUTHORIZED
    
@router.get("/v1/rooms")
def get_sala(current_user: dict = Depends(verify_jwt)): #Almacena la información del usuario (mail entre otras cosas)
    if current_user:
       return get_rooms()
    else:
        raise HTTP_401_UNAUTHORIZED


@router.post("/v1/reserve/request")
async def request(reserve: ReservaSQL, current_user: dict = Depends(verify_jwt)):
    try:
        response = reserve_request(reserve, current_user)
        if response:
            return response
        else:
            raise HTTP_500_INTERNAL_SERVER_ERROR
    except HTTPException as http_exc:
        return http_exc

@router.post("/v1/reserve/search")
def search_reservations(params: ReservaSearchSQL, current_user: dict = Depends(verify_jwt)):
    if current_user:
        reservations = fetch_reservations(params)
        if reservations:
            return reservations
        else:
            return {"message": "No se encontraron reservas con los parámetros proporcionados"}
    else:
        raise HTTP_401_UNAUTHORIZED

@router.get("/v1/reserve/{roomCode}/schedule/{date}")
def get_room_schedule(roomCode: str, date: str, current_user: dict = Depends(verify_jwt)):
    if current_user:
        schedule = fetch_room_schedule(roomCode, date)
        if schedule:
            return schedule
        else:
            return {"message": "No hay reservas para esta sala en la fecha proporcionada"}
    else:
        raise HTTP_401_UNAUTHORIZED
    
@router.delete("/v1/reserve/{token}/cancel")
async def cancel_reservation(token: str, current_user:dict = Depends(verify_jwt)):
    if current_user:
        result = cancel_reservation_token(token)
        if result:
            return result  # Retornar el mensaje de éxito o error desde la función fetch_reservations
    else:
        raise HTTP_401_UNAUTHORIZED