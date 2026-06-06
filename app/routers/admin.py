from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.auth.auth import verify_admin, TokenData
from app.database import get_all_users, update_user, delete_user, get_user_by_id, get_all_orders, update_order_state

router = APIRouter(prefix="/admin", tags=["Admin"])


class UserUpdate(BaseModel):
    email: Optional[str] = None
    nombre: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    estado: int


# Routers para usuarios

@router.get("/usuarios/", status_code=status.HTTP_200_OK)
async def list_users(admin: TokenData = Depends(verify_admin)):
    return get_all_users()


@router.put("/usuarios/{user_id}/", status_code=status.HTTP_200_OK)
async def update_user_data(
    user_id: int,
    datos: UserUpdate,
    admin: TokenData = Depends(verify_admin)
):
    if not get_user_by_id(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    update_user(user_id, datos.model_dump(exclude_none=True))

    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return {
        "id": user.id,
        "email": user.email,
        "nombre": user.nombre,
        "tipo": user.tipo,
        "username": user.username,
    }


@router.delete("/usuarios/{user_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(
    user_id: int,
    admin: TokenData = Depends(verify_admin)
):
    if not get_user_by_id(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    success = delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el usuario porque tiene pedidos, reservas o eventos asociados"
        )
    return None


# Routers para orders

@router.get("/orders/", status_code=status.HTTP_200_OK)
async def list_all_orders(admin: TokenData = Depends(verify_admin)):
    return get_all_orders()


@router.patch("/orders/{numero_pedido}/", status_code=status.HTTP_200_OK)
async def update_order(
    numero_pedido: int,
    datos: OrderStatusUpdate,
    admin: TokenData = Depends(verify_admin)
):
    if datos.estado not in (1, 2, 3, 4):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estado inválido (debe ser 1-4)")

    success = update_order_state(numero_pedido, datos.estado)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    return {"numero_pedido": numero_pedido, "estado": datos.estado}