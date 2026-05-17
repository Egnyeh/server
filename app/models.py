from datetime import date
import string
from sys import float_repr_style
from typing import Optional
from pydantic import BaseModel


# ========= USER MODELS ===========

class UserBase(BaseModel):
    email: str
    password: str


class UserCreate(UserBase):
    username: str
    nombre: str
    password: str
    tipo: str = "cliente" #Por defecto va a definirse como cliente


class UserDb(UserBase):
    id: int
    nombre: str
    password: str #hashed
    tipo: str


class ClienteDb(UserDb):
    username: str


class AdminDb(UserDb):
    username: str
    fecha_alta: date


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    nombre: str
    tipo: str



# =========== PRODUCT MODELS =============

class ProductBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None 
    #Optional, de la libreria typing, lo que hace es que ese campo pueda ser None, no obligatorio
    #con el igual, lo que hacemos es darle un valor por defecto, como hemos hecho en tipo con cliente
    categoria: str
    precio_unitario: float
    stock: int = 0
    disponibilidad: bool = True #Como default lo marcamos como disponible


class ProductCreate(ProductBase): # Para que el admin cree productos
    pass


class ProductUpdate(BaseModel): #Al actualizar productos, los campos pueden ser none puesto que no es necesario actualizarlos todos
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    precio_unitario: Optional[float] = None
    stock: Optional[int] = None

class ProductOut(ProductBase):
    id: int

class ProductInOrder(BaseModel):
    id: int
    cantidad: int


#============= ORDER MODELS ================

class OrderLineCreate(BaseModel):
    id_producto: int
    cantidad: int


class OrderLineOut(BaseModel):
    id: int
    numero_pedido: int
    id_producto: int
    precio: float
    cantidad: int


class OrderCreate(BaseModel): #Se crea un pedido a base de una lista de lineas de pedido (productos)
    lineas: list[ProductInOrder]


class OrderOut(BaseModel):
    numero_pedido: int
    id_usuario: int
    fecha_pedido: date
    precio_total: float
    estado: int
    lineas: Optional[list[OrderLineOut]] = None #Al obtener un pedido, las lineas pueden ser none


#============== AUTENTICATION MODELS ===============

class Token(BaseModel): #respuesta del login
    access_token: str
    token_type: str = "bearer" # Tipo: "portador" (estandar para JWT), indica que el token debe ser enviado en la cabecera Authorization


class TokenData(BaseModel): #datos dentro del token JWT
    user_id: int
    username: str
    tipo: str


#============== RESERVAS MODELS ===============
class ReservaJuegoCreate(BaseModel):
    id_juego: int
    fecha_inicio: date
    fecha_fin: date

class ReservaEventoCreate(BaseModel):
    id_evento: int

class JuegoCreate(BaseModel):
    nombre: str
    precio_dia: float

class EventoCreate(BaseModel):
    nombre_evento: str
    fecha: date