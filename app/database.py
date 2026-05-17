from datetime import date
from typing import Iterable
import mariadb
from app.auth.auth import get_hash_password
from app.models import (
    AdminDb,
    ClienteDb,
    OrderLineOut,
    ProductCreate,
    ProductUpdate,
    UserCreate,
    UserOut,
    ProductOut,
)


db_config = {
    "host": "myapidb",
    "port": 3306,
    "user": "myapi",
    "password": "myapi",
    "database": "myapi",
}

# ------------- USER FUNCTIONS --------------


def insert_user(user: UserCreate) -> UserOut:  # ✅ Cambiado de int a UserOut
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            hashed_password = get_hash_password(user.password)
            # Consultas preparadas para evitar SQL Injection
            sql_usuario = "insert into usuario (email, nombre, password, tipo) values (?, ?, ?, ?)"
            values = (user.email, user.nombre, hashed_password, user.tipo)
            cursor.execute(sql_usuario, values)
            user_id = cursor.lastrowid

            if user.tipo == "cliente":
                sql_cliente = "insert into cliente (id, username) values (?, ?)"
                values_cliente = (user_id, user.username)
                cursor.execute(sql_cliente, values_cliente)
            elif user.tipo == "admin":
                sql_admin = "insert into admin (id, username, fecha_alta) values (?, ?, CURDATE())"
                values_admin = (user_id, user.username)
                cursor.execute(sql_admin, values_admin)

            conn.commit()

            return UserOut(
                id=user_id,
                email=user.email,
                username=user.username,
                nombre=user.nombre,
                tipo=user.tipo,
            )


def get_user_by_username(username: str) -> ClienteDb | AdminDb | None:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql_cliente = """ 
                SELECT u.id, u.email, u.nombre, u.password, u.tipo, c.username
                FROM usuario u
                INNER JOIN cliente c ON u.id = c.id
                WHERE c.username = ?
            """
            cursor.execute(sql_cliente, (username,))
            row = cursor.fetchone()

            if row:
                return ClienteDb(
                    id=row[0],
                    email=row[1],
                    nombre=row[2],
                    password=row[3],
                    tipo=row[4],
                    username=row[5],
                )

            sql_admin = """
                SELECT u.id, u.email, u.nombre, u.password, u.tipo, a.username, a.fecha_alta
                FROM usuario u
                INNER JOIN admin a ON u.id = a.id
                WHERE a.username = ?
                """
            cursor.execute(sql_admin, (username,))
            row = cursor.fetchone()

            if row:
                return AdminDb(
                    id=row[0],
                    email=row[1],
                    nombre=row[2],
                    password=row[3],
                    tipo=row[4],
                    username=row[5],
                    fecha_alta=row[6],
                )

            return None


def get_user_by_id(user_id: int) -> ClienteDb | AdminDb | None:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql_cliente = """ 
                SELECT u.id, u.email, u.nombre, u.password, u.tipo, c.username
                FROM usuario u
                INNER JOIN cliente c ON u.id = c.id
                WHERE u.id = ?
            """
            cursor.execute(sql_cliente, (user_id,))
            row = cursor.fetchone()

            if row:
                return ClienteDb(
                    id=row[0],
                    email=row[1],
                    nombre=row[2],
                    password=row[3],
                    tipo=row[4],
                    username=row[5],
                )

            sql_admin = """
                SELECT u.id, u.email, u.nombre, u.password, u.tipo, a.username, a.fecha_alta
                FROM usuario u
                INNER JOIN admin a ON u.id = a.id
                WHERE u.id = ?
                """
            cursor.execute(sql_admin, (user_id,))
            row = cursor.fetchone()

            if row:
                return AdminDb(
                    id=row[0],
                    email=row[1],
                    nombre=row[2],
                    password=row[3],
                    tipo=row[4],
                    username=row[5],
                    fecha_alta=row[6],
                )

            return None


# ------------- PRODUCT FUNCTIONS --------------


def get_all_products() -> list[ProductOut]:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql = "SELECT id, nombre, descripcion, categoria, precio_unitario, stock, disponibilidad FROM producto"
            cursor.execute(sql)
            rows = cursor.fetchall()

            products = []
            for row in rows:
                products.append(
                    ProductOut(
                        id=row[0],
                        nombre=row[1],
                        descripcion=row[2],
                        categoria=row[3],
                        precio_unitario=row[4],
                        stock=row[5],
                        disponibilidad=row[6],
                    )
                )
            return products


def get_product_by_id(product_id: int) -> ProductOut | None:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql = "SELECT id, nombre, descripcion, categoria, precio_unitario, stock, disponibilidad FROM producto WHERE id = ?"
            cursor.execute(sql, (product_id,))
            row = cursor.fetchone()

            if row:
                return ProductOut(
                    id=row[0],
                    nombre=row[1],
                    descripcion=row[2],
                    categoria=row[3],
                    precio_unitario=row[4],
                    stock=row[5],
                    disponibilidad=row[6],
                )
            return None


def search_products_by_name(nombre: str) -> list[ProductOut]:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql = """
                SELECT id, nombre, descripcion, categoria, precio_unitario, stock, disponibilidad 
                FROM producto 
                WHERE nombre LIKE ?
            """
            # El % permite buscar coincidencias parciales
            cursor.execute(sql, (f"%{nombre}%",))
            rows = cursor.fetchall()

            products = []
            for row in rows:
                products.append(
                    ProductOut(
                        id=row[0],
                        nombre=row[1],
                        descripcion=row[2],
                        categoria=row[3],
                        precio_unitario=row[4],
                        stock=row[5],
                        disponibilidad=row[6],
                    )
                )
            return products


def insert_product(product: ProductCreate) -> int:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO producto (nombre, descripcion, categoria, precio_unitario, stock, disponibilidad)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            values = (
                product.nombre,
                product.descripcion,
                product.categoria,
                product.precio_unitario,
                product.stock,
                product.disponibilidad,
            )
            cursor.execute(sql, values)
            conn.commit()
            return cursor.lastrowid


def update_product(product_id: int, product: ProductUpdate) -> bool:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            campos = []
            valores = []

            if product.nombre is not None:
                campos.append("nombre = ?")
                valores.append(product.nombre)
            if product.descripcion is not None:
                campos.append("descripcion = ?")
                valores.append(product.descripcion)
            if product.categoria is not None:
                campos.append("categoria = ?")
                valores.append(product.categoria)
            if product.precio_unitario is not None:
                campos.append("precio_unitario = ?")
                valores.append(product.precio_unitario)
            if product.stock is not None:
                campos.append("stock = ?")
                valores.append(product.stock)
            if product.disponibilidad is not None:
                campos.append("disponibilidad = ?")
                valores.append(product.disponibilidad)

            if not campos:
                return False  # Si no hay nada que actualizar

            valores.append(product_id)
            sql = f"UPDATE producto SET {', '.join(campos)} WHERE id = ?"
            cursor.execute(sql, valores)  # ✅ AÑADIDO: Faltaba ejecutar el SQL
            conn.commit()
            return (
                cursor.rowcount > 0
            )  # Devuelve true si actualizamos al menos una fila


def delete_product(product_id: int) -> bool:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql = "DELETE FROM producto WHERE id = ?"
            cursor.execute(sql, (product_id,))
            conn.commit()
            return cursor.rowcount > 0  # Devuelve true si borramos al menos una fila


# ------------- ORDER FUNCTIONS --------------


def add_product_to_order(
    numero_pedido: int, id_producto: int, cantidad: int, precio: float | None = None
) -> int | None:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            # Comprobar si el pedido existe
            cursor.execute(
                "SELECT numero_pedido FROM pedido WHERE numero_pedido = ? LIMIT 1", 
                (numero_pedido,),
            )
            if cursor.fetchone() is None:
                return None

            # Comprobar si el producto existe
            cursor.execute(
                "SELECT precio_unitario FROM producto WHERE id = ? LIMIT 1",
                (id_producto,),
            )
            result = cursor.fetchone()
            if result is None:
                return None

            if precio is None:
                precio = result[0]

            sql = """
                INSERT INTO linea_pedido (numero_pedido, id_producto, precio, cantidad)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(sql, (numero_pedido, id_producto, precio, cantidad))
            conn.commit()

            return cursor.lastrowid


def create_order_with_items(order: dict, items: Iterable[dict]) -> int | None:
    try:
        with mariadb.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                sql_pedido = """
                    INSERT INTO pedido(id_usuario, fecha_pedido, precio_total, estado)
                    VALUES (?, ?, ?, ?)
                """  

                values_order = (
                    order["id_usuario"],
                    order["fecha_pedido"],
                    order["precio_total"],
                    order["estado"],
                )
                cursor.execute(sql_pedido, values_order)
                numero_pedido = cursor.lastrowid

                # Insertar productos
                if items:
                    sql_item = """
                        INSERT INTO linea_pedido (numero_pedido, id_producto, precio, cantidad)
                        VALUES (?, ?, ?, ?)
                    """
                    for item in items:
                        id_producto = item["id_producto"]
                        cantidad = item["cantidad"]
                        precio = item.get("precio")
                        cursor.execute(
                            sql_item, (numero_pedido, id_producto, precio, cantidad)
                        )
                        cursor.execute(
                            "UPDATE producto SET stock = stock - ? WHERE id = ?",
                            (cantidad, id_producto)
                        )

                conn.commit()
                return numero_pedido
    except mariadb.Error as e:
        print(f"Error al crear pedido: {e}")
        return None


def get_orders_by_user(user_id: int) -> list[dict]:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql = """
                SELECT p.numero_pedido, p.id_usuario, p.fecha_pedido, p.precio_total, p.estado
                FROM pedido p
                WHERE p.id_usuario = ?
            """  
            cursor.execute(sql, (user_id,))
            rows = cursor.fetchall()

            orders = []
            for row in rows:
                orders.append(
                    {
                        "numero_pedido": row[0],
                        "id_usuario": row[1],
                        "fecha_pedido": row[2],  
                        "precio_total": row[3],
                        "estado": row[4],
                    }
                )
            return orders

def get_order_lines(numero_pedido: int) -> list[OrderLineOut]:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            sql = """
                SELECT id, numero_pedido, id_producto, precio, cantidad
                FROM linea_pedido
                WHERE numero_pedido = ?
            """
            cursor.execute(sql, (numero_pedido,))
            rows = cursor.fetchall()

            return [
                OrderLineOut(
                    id=row[0],
                    numero_pedido=row[1],
                    id_producto=row[2],
                    precio=row[3],
                    cantidad=row[4],
                )
                for row in rows
            ]
        
# ------------- RESERVAS FUNCTIONS --------------

def get_all_juegos() -> list[dict]:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nombre, precio_dia FROM juego")
            rows = cursor.fetchall()
            return [{"id": row[0], "nombre": row[1], "precio_dia": row[2]} for row in rows]


def get_all_eventos() -> list[dict]:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, id_admin, nombre_evento, fecha FROM evento")
            rows = cursor.fetchall()
            return [{"id": row[0], "id_admin": row[1], "nombre_evento": row[2], "fecha": row[3]} for row in rows]


def create_reserva_juego(user_id: int, id_juego: int, fecha_inicio, fecha_fin) -> int | None:
    try:
        with mariadb.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                # Obtener precio_dia del juego
                cursor.execute("SELECT precio_dia FROM juego WHERE id = ?", (id_juego,))
                row = cursor.fetchone()
                if not row:
                    return None
                precio_dia = row[0]

                # Calcular días y precio total
                dias = (fecha_fin - fecha_inicio).days
                if dias <= 0:
                    return None
                precio_total = precio_dia * dias

                # Insertar reserva base
                cursor.execute(
                    "INSERT INTO reserva (id_usuario, tipo, cantidad, fecha_reserva) VALUES (?, 1, ?, NOW())",
                    (user_id, dias)
                )
                id_reserva = cursor.lastrowid

                # Insertar reserva_juego
                cursor.execute(
                    "INSERT INTO reserva_juego (id_reserva, id_juego, fecha_inicio, fecha_fin, precio_total) VALUES (?, ?, ?, ?, ?)",
                    (id_reserva, id_juego, fecha_inicio, fecha_fin, precio_total)
                )
                conn.commit()
                return id_reserva
    except mariadb.Error as e:
        print(f"Error al crear reserva de juego: {e}")
        return None


def create_reserva_evento(user_id: int, id_evento: int) -> int | None:
    try:
        with mariadb.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                # Verificar que el evento existe
                cursor.execute("SELECT id FROM evento WHERE id = ?", (id_evento,))
                if not cursor.fetchone():
                    return None

                # Insertar reserva base
                cursor.execute(
                    "INSERT INTO reserva (id_usuario, tipo, cantidad, fecha_reserva) VALUES (?, 2, 1, NOW())",
                    (user_id,)
                )
                id_reserva = cursor.lastrowid

                # Insertar reserva_evento
                cursor.execute(
                    "INSERT INTO reserva_evento (id_reserva, id_evento) VALUES (?, ?)",
                    (id_reserva, id_evento)
                )
                conn.commit()
                return id_reserva
    except mariadb.Error as e:
        print(f"Error al crear reserva de evento: {e}")
        return None


def get_reservas_by_user(user_id: int) -> list[dict]:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            # Reservas de juegos
            cursor.execute("""
                SELECT r.id, r.fecha_reserva, j.nombre, rj.fecha_inicio, rj.fecha_fin, rj.precio_total
                FROM reserva r
                JOIN reserva_juego rj ON r.id = rj.id_reserva
                JOIN juego j ON rj.id_juego = j.id
                WHERE r.id_usuario = ?
            """, (user_id,))
            juegos = [
                {
                    "id_reserva": row[0],
                    "fecha_reserva": row[1],
                    "tipo": "juego",
                    "nombre": row[2],
                    "fecha_inicio": row[3],
                    "fecha_fin": row[4],
                    "precio_total": row[5],
                }
                for row in cursor.fetchall()
            ]

            # Reservas de eventos
            cursor.execute("""
                SELECT r.id, r.fecha_reserva, e.nombre_evento, e.fecha
                FROM reserva r
                JOIN reserva_evento re ON r.id = re.id_reserva
                JOIN evento e ON re.id_evento = e.id
                WHERE r.id_usuario = ?
            """, (user_id,))
            eventos = [
                {
                    "id_reserva": row[0],
                    "fecha_reserva": row[1],
                    "tipo": "evento",
                    "nombre": row[2],
                    "fecha_evento": row[3],
                }
                for row in cursor.fetchall()
            ]

            return juegos + eventos

# ------------- EVENT FUNCTIONS --------------
def insert_juego(nombre: str, precio_dia: float) -> int | None:
    try:
        with mariadb.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO juego (nombre, precio_dia) VALUES (?, ?)",
                    (nombre, precio_dia)
                )
                conn.commit()
                return cursor.lastrowid
    except mariadb.Error as e:
        print(f"Error al insertar juego: {e}")
        return None


def insert_evento(id_admin: int, nombre_evento: str, fecha: date) -> int | None:
    try:
        with mariadb.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO evento (id_admin, nombre_evento, fecha) VALUES (?, ?, ?)",
                    (id_admin, nombre_evento, fecha)
                )
                conn.commit()
                return cursor.lastrowid
    except mariadb.Error as e:
        print(f"Error al insertar evento: {e}")
        return None

# ------------- ADMIN USER MANAGEMENT --------------

def get_all_users() -> list[dict]:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.email, u.nombre, u.tipo,
                    COALESCE(c.username, a.username) as username
                FROM usuario u
                LEFT JOIN cliente c ON u.id = c.id
                LEFT JOIN admin a ON u.id = a.id
            """)
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "email": row[1],
                    "nombre": row[2],
                    "tipo": row[3],
                    "username": row[4],
                }
                for row in rows
            ]


def update_user(user_id: int, datos: dict) -> bool:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            campos = []
            valores = []

            if datos.get("email"):
                campos.append("email = ?")
                valores.append(datos["email"])
            if datos.get("nombre"):
                campos.append("nombre = ?")
                valores.append(datos["nombre"])

            if not campos:
                return False

            valores.append(user_id)
            sql = f"UPDATE usuario SET {', '.join(campos)} WHERE id = ?"
            cursor.execute(sql, valores)
            conn.commit()
            return cursor.rowcount > 0


def delete_user(user_id: int) -> bool:
    with mariadb.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM usuario WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0