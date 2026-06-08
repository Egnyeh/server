from datetime import date
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from app.models import EventoCreate, EventoUpdate, JuegoCreate, JuegoUpdate, ReservaEventoCreate, ReservaJuegoCreate
from app.auth.auth import get_current_user, verify_admin, TokenData
from app.database import (
    delete_evento,
    delete_juego,
    get_all_juegos,
    get_all_eventos,
    create_reserva_juego,
    create_reserva_evento,
    get_reservas_by_user,
    insert_evento,
    update_evento,
    delete_evento,
    insert_juego,
    update_juego,
    delete_juego
)


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

@router.put("/juegos/{id_juego}/", status_code=status.HTTP_200_OK)
async def update_juego_endpoint(
    id_juego: int,
    juego: JuegoUpdate,
    admin: TokenData = Depends(verify_admin)
):
    success = update_juego(id_juego, juego.nombre, juego.precio_dia)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Juego no encontrado")
    return {"id": id_juego, "nombre": juego.nombre, "precio_dia": juego.precio_dia}


@router.delete("/juegos/{id_juego}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_juego_endpoint(
    id_juego: int,
    admin: TokenData = Depends(verify_admin)
):
    success = delete_juego(id_juego)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el juego porque tiene reservas asociadas"
        )
    return None

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

@router.put("/eventos/{id_evento}/", status_code=status.HTTP_200_OK)
async def update_evento_endpoint(
    id_evento: int,
    evento: EventoUpdate,
    admin: TokenData = Depends(verify_admin)
):
    success = update_evento(id_evento, evento.nombre_evento, evento.fecha)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado")
    return {"id": id_evento, "nombre_evento": evento.nombre_evento, "fecha": evento.fecha}


@router.delete("/eventos/{id_evento}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evento_endpoint(
    id_evento: int,
    admin: TokenData = Depends(verify_admin)
):
    success = delete_evento(id_evento)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el evento porque tiene inscripciones asociadas"
        )
    return None


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