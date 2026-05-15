from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.models import OrderOut, UserOut, UserDb, UserCreate
from app.auth.auth import (
    TokenData,
    create_access_token,
    Token,
    verify_password,
    oauth2_scheme,
    decode_token,
)
from app.database import get_user_by_username, insert_user, get_user_by_id, get_orders_by_user, get_order_lines

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/signup/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    if get_user_by_username(user.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El usuario ya existe")
    return insert_user(user)


@router.post("/login/", response_model=Token, status_code=status.HTTP_200_OK)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not form_data.username or not form_data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")

    user = get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")

    token_data = {"user_id": user.id, "username": user.username, "tipo": user.tipo}
    return Token(access_token=create_access_token(token_data), token_type="bearer")


@router.get("/me/", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_me(token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)
    user = get_user_by_id(data.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return UserOut(
        id=user.id,
        email=user.email,
        username=user.username,
        nombre=user.nombre,  
        tipo=user.tipo,
    )


@router.get("/{user_id}/orders/", response_model=list[OrderOut], status_code=status.HTTP_200_OK)
async def get_user_orders(user_id: int, token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)
    if data.user_id != user_id and data.tipo != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")

    orders = get_orders_by_user(user_id)
    return [OrderOut(**o, lineas=get_order_lines(o["numero_pedido"])) for o in orders]


@router.get("/{user_id}/orders/{numero_pedido}/", response_model=OrderOut, status_code=status.HTTP_200_OK)
async def get_user_order_by_id(user_id: int, numero_pedido: int, token: str = Depends(oauth2_scheme)):
    data: TokenData = decode_token(token)
    if data.user_id != user_id and data.tipo != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")

    orders = get_orders_by_user(user_id)
    order = next((o for o in orders if o["numero_pedido"] == numero_pedido), None) 
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    return OrderOut(**order, lineas=get_order_lines(numero_pedido))