from datetime import date
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel

from app.auth.auth import get_current_user, verify_admin, TokenData
from app.database import (
    get_all_juegos,
    get_all_eventos,
    create_reserva_juego,
    create_reserva_evento,
    get_reservas_by_user,
    insert_evento,
    insert_juego,
)
from server.app.models import EventoCreate, JuegoCreate, ReservaEventoCreate, ReservaJuegoCreate

router = APIRouter(prefix="/reservas", tags=["Reservas"])


# ---- Juegos ----

@router.get("/juegos/", status_code=status.HTTP_200_OK)
async def get_juegos():
    return get_all_juegos()

@router.post("/juegos/", status_code=status.HTTP_201_CREATED)
async def create_juego(juego: JuegoCreate, admin: TokenData = Depends(verify_admin)):
    id_juego = insert_juego(juego.nombre, juego.precio_dia)
    if not id_juego:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el juego")
    return {"id": id_juego, "nombre": juego.nombre, "precio_dia": juego.precio_dia}


# ---- Eventos ----

@router.get("/eventos/", status_code=status.HTTP_200_OK)
async def get_eventos():
    return get_all_eventos()

@router.post("/eventos/", status_code=status.HTTP_201_CREATED)
async def create_evento(evento: EventoCreate, admin: TokenData = Depends(verify_admin)):
    id_evento = insert_evento(admin.user_id, evento.nombre_evento, evento.fecha)
    if not id_evento:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el evento")
    return {"id": id_evento, "nombre_evento": evento.nombre_evento, "fecha": evento.fecha}


# ---- Reservas ----

@router.post("/juego/", status_code=status.HTTP_201_CREATED)
async def reservar_juego(
    reserva: ReservaJuegoCreate,
    user: TokenData = Depends(get_current_user)
):
    id_reserva = create_reserva_juego(user.user_id, reserva.id_juego, reserva.fecha_inicio, reserva.fecha_fin)
    if not id_reserva:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear la reserva. Verifica que el juego existe y las fechas son válidas"
        )
    return {"id_reserva": id_reserva, "mensaje": "Reserva de juego creada correctamente"}


@router.post("/evento/", status_code=status.HTTP_201_CREATED)
async def reservar_evento(
    reserva: ReservaEventoCreate,
    user: TokenData = Depends(get_current_user)
):
    id_reserva = create_reserva_evento(user.user_id, reserva.id_evento)
    if not id_reserva:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear la reserva. Verifica que el evento existe"
        )
    return {"id_reserva": id_reserva, "mensaje": "Reserva de evento creada correctamente"}


@router.get("/", status_code=status.HTTP_200_OK)
async def get_mis_reservas(user: TokenData = Depends(get_current_user)):
    return get_reservas_by_user(user.user_id)