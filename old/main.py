import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, unquote

import psycopg
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from psycopg.rows import dict_row

app = FastAPI(title="E-Shop-СI-CD-1.0.1")


def _db_connect_kwargs() -> dict:
    """
    Railway обычно задаёт DATABASE_URL при связи с Postgres.
    Иначе — отдельные DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME.
    """
    raw = (os.getenv("DATABASE_URL") or "").replace("postgres://", "postgresql://", 1)
    if raw:
        u = urlparse(raw)
        kw: dict = {
            "host": u.hostname or "localhost",
            "port": u.port or 5432,
            "user": unquote(u.username or ""),
            "password": unquote(u.password or ""),
            "dbname": (u.path or "/").lstrip("/") or "railway",
        }
    else:
        kw = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "user": os.getenv("DB_USER", "app"),
            "password": os.getenv("DB_PASSWORD", "app"),
            "dbname": os.getenv("DB_NAME", "eshop"),
        }
    host = kw.get("host") or ""
    if host not in ("localhost", "127.0.0.1", "::1"):
        kw["sslmode"] = os.getenv("PGSSLMODE", "require")
    return kw


def get_db_connection():
    return psycopg.connect(**_db_connect_kwargs(), row_factory=dict_row)


@app.get("/products")
async def get_products():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, price, description, created_at FROM video_cards ORDER BY id"
            )
            return [{**dict(r), "price": float(r["price"])} for r in cur.fetchall()]
    finally:
        conn.close()


@app.get("/health")
async def health():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as count FROM video_cards")
            count = cur.fetchone()["count"]
            return {"status": "ok", "products": count}
    finally:
        conn.close()
