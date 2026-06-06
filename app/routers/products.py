from math import prod
from fastapi import APIRouter, Depends, status, HTTPException

from app.models import ProductCreate, ProductUpdate, ProductOut, TokenData
from app.auth.auth import oauth2_scheme, decode_token, verify_admin
from app.database import (
    get_all_products,
    get_product_by_id,
    search_products_by_name,
    insert_product,
    update_product as db_update_product, #He tenido que renombrar esto para que no colisione con el nombre del endpoint, que se llama igual xd y me de error
    delete_product as db_delete_product,
)

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("/", response_model=list[ProductOut], status_code=status.HTTP_200_OK)
async def get_products(nombre: str | None = None): 
    if nombre:
        products = search_products_by_name(nombre) 
    else:
        products = get_all_products()
    return products


@router.get("/{product_id}/", response_model=ProductOut, status_code=status.HTTP_200_OK)
async def get_product(product_id: int):
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductOut, status_code=status.HTTP_200_OK)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    admin: TokenData = Depends(verify_admin) 
):
    existing_product = get_product_by_id(product_id)
    if not existing_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    success = db_update_product(product_id, product)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update product")

    updated_product = get_product_by_id(product_id)
    return updated_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    admin: TokenData = Depends(verify_admin)
):
    existing_product = get_product_by_id(product_id)
    if not existing_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    success = db_delete_product(product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el producto porque tiene pedidos asociados"
        )
    return None


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    admin: TokenData = Depends(verify_admin)
):
    # Comprobamos que el producto no exista ya
    existing_products = search_products_by_name(product.nombre)
    for existing in existing_products:
        if existing.nombre.lower() == product.nombre.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Ya existe un producto con ese nombre"
            )
    
    # Validaciones
    if product.precio_unitario <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El precio unitario debe ser mayor que 0"
        )
    
    if product.stock < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El stock no puede ser negativo"
        )
    
    # Insertar producto
    product_id = insert_product(product)
    if not product_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el producto"
        )
    
    # Devolver producto una vez creado
    new_product = get_product_by_id(product_id)
    return new_product
