# Implementar sistema de guardado de ubicaciones favoritas.
from T3 import get_conn

def save_favorite(ciudad, lat, lon):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO favorites (ciudad, lat, lon) VALUES (?, ?, ?)", (ciudad, lat, lon))
    conn.commit()
    conn.close()

def get_favorites():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT ciudad, lat, lon FROM favorites")
    return [{"ciudad": r[0], "lat": r[1], "lon": r[2]} for r in cursor.fetchall()]
