import json
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime


class Product(BaseModel):
    name: str
    price: float
    description: str
    created_at: str


app = FastAPI(title="E-Shop-СI-CD")

with open(Path(__file__).parent / "shop.json", "r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)

CART = []
ORDERS = []

@app.get("/products")
async def get_products():
    return PRODUCTS


@app.get("/product/{pid}")
async def get_product(pid: int):
    if 0 <= pid < len(PRODUCTS):
        return PRODUCTS[pid]
    raise HTTPException(status_code=404, detail="Not found")


@app.get("/health")
async def health():
    # аннотация
    return {"status": "ok", "products": len(PRODUCTS)}

@app.get("/search")
async def search(q: str = Query(..., min_length=1)):
    """Поиск товаров по подстроке в названии (q). Регистр не учитывается."""
    return [p for p in PRODUCTS if q.lower() in p ["name"].lower()]


@app.post("/cart/add")
async def add_cart(pid: int, qty: int = 1):
    """Добавляет товар в корзину по id (pid) и количеству (qty). 404 при неверном pid."""
    if not (0 <= pid < len(PRODUCTS)):
        raise HTTPException(status_code=404)
    p = PRODUCTS[pid]
    CART.append({"name": p["name"], "qty": qty, "price": p["price"] * qty})
    return {"ok": True}


@app.get("/cart")
async def get_cart():
    """Возвращает содержимое корзины и общую сумму."""
    return {"items": CART, "total": sum(i["price"] for i in CART)}


@app.delete("/cart")
async def clear_cart():
    """Очищает корзину полностью."""
    CART.clear()
    return {"ok": True}


@app.post("/checkout")
async def checkout():
    """Оформляет заказ: сохраняет текущую корзину в заказы, очищает корзину. 400 если корзина пуста."""
    if not CART:
        raise HTTPException(status_code=400)
    total = sum(item["price"] for item in CART)
    order = {"id": len(ORDERS), "items": CART.copy(), "total": total, "created_at": datetime.now().isoformat()}
    ORDERS.append(order)
    CART.clear()
    return order


@app.get("/orders")
async def get_orders():
    """Возвращает список всех оформленных заказов."""
    return ORDERS