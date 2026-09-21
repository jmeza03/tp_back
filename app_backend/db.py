import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


def get_connection():
    """Abre y devuelve una conexión a MySQL."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def query_all(sql, params=None):
    """Ejecuta un SELECT y devuelve todas las filas como lista de dicts."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        return cur.fetchall()
    finally:
        conn.close()


def query_one(sql, params=None):
    """Ejecuta un SELECT y devuelve una fila (dict) o None."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        return cur.fetchone()
    finally:
        conn.close()


def execute(sql, params=None):
    """Ejecuta INSERT/UPDATE/DELETE. Devuelve lastrowid o rowcount."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        return cur.lastrowid or cur.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()