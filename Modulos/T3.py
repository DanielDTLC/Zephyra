# services/db_service.py
import pyodbc
from T1 import DB_CONN_STR

def get_conn():
    return pyodbc.connect(DB_CONN_STR)

def save_historical(ciudad, temp, hum, estado, lat=None, lon=None):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO historical (ciudad, temperatura, humedad, estado, lat, lon) VALUES (?, ?, ?, ?, ?, ?)",
        (ciudad, temp, hum, estado, lat, lon)
    )
    conn.commit()
    conn.close()
