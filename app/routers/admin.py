from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.auth.auth import verify_admin, TokenData
from app.database import get_all_users, update_user, delete_user, get_user_by_id

router = APIRouter(prefix="/admin", tags=["Admin"])


class UserUpdate(BaseModel):
    email: Optional[str] = None
    nombre: Optional[str] = None


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

    success = update_user(user_id, datos.model_dump(exclude_none=True))
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nada que actualizar o error al actualizar")

    return get_user_by_id(user_id)


@router.delete("/usuarios/{user_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(
    user_id: int,
    admin: TokenData = Depends(verify_admin)
):
    # Evitar que el admin se elimine a sí mismo
    if not get_user_by_id(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    success = delete_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el usuario")
    return None