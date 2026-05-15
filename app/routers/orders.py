from datetime import date
from operator import add
from venv import create
from webbrowser import get
from fastapi import APIRouter, Depends, status, HTTPException


from app.models import OrderCreate, OrderOut, ProductOut, TokenData, ProductInOrder
from app.auth.auth import decode_token, get_current_user, oauth2_scheme, TokenData
from app.database import get_order_lines, create_order_with_items, get_order_lines, get_orders_by_user, get_product_by_id
from app.routers import products

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", response_model=list[OrderOut], status_code=status.HTTP_200_OK)
async def get_all_orders(user: TokenData = Depends(get_current_user)):
    orders = get_orders_by_user(user.user_id)
    return [OrderOut(**o, lineas=get_order_lines(o["numero_pedido"])) for o in orders]  

@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    user: TokenData = Depends(get_current_user)
):
    if not order_data.lineas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El pedido debe contener al menos una línea"
        )

    total_price = 0.0
    items_to_insert = []

    for linea in order_data.lineas:
        producto = get_product_by_id(linea.id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El producto con id {linea.id} no existe"
            )
        if not producto.disponibilidad or producto.stock < linea.cantidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El producto con id {linea.id} no tiene stock suficiente"
            )

        total_price += producto.precio_unitario * linea.cantidad
        items_to_insert.append({
            "id_producto": linea.id,
            "cantidad": linea.cantidad,
            "precio": producto.precio_unitario,
        })

    order_dict = {
        "id_usuario": user.user_id,
        "fecha_pedido": date.today(),
        "precio_total": total_price,
        "estado": 1,
    }

    numero_pedido = create_order_with_items(order_dict, items_to_insert)
    if not numero_pedido:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el pedido"
        )

    lineas_insertadas = get_order_lines(numero_pedido)

    return OrderOut(
        numero_pedido=numero_pedido,
        id_usuario=user.user_id,
        fecha_pedido=date.today(),
        precio_total=total_price,
        estado=1,
        lineas=lineas_insertadas,
    )


@router.get("/{numero_pedido}/", response_model=OrderOut, status_code=status.HTTP_200_OK)
async def get_order(
    numero_pedido: int,
    user: TokenData = Depends(get_current_user)
):
    orders = get_orders_by_user(user.user_id)
    order = next((o for o in orders if o["numero_pedido"] == numero_pedido), None)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    lineas = get_order_lines(numero_pedido)
    return OrderOut(**order, lineas=lineas)

