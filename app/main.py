from fastapi import FastAPI

from app.routers import users, products, orders, reservas, admin

app = FastAPI(debug=True)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(reservas.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to 2tgames API",
        "version": "1.0"
        }
