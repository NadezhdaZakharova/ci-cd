from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    """Проверка endpoint /health"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_products():
    """Проверка endpoint /products"""
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_search():
    response = client.get("/search?q=5090")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_cart_add():
    response = client.post("/cart/add?pid=0&qty=2")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_cart_get():
    response = client.get("/cart")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()


def test_cart_clear():
    response = client.delete("/cart")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_checkout():
    client.post("/cart/add?pid=0&qty=1")
    response = client.post("/checkout")
    assert response.status_code == 200
    assert "id" in response.json()
    assert "total" in response.json()


def test_checkout_empty():
    client.delete("/cart")
    response = client.post("/checkout")
    assert response.status_code == 400


def test_orders():
    response = client.get("/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
