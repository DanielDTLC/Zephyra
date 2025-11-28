# app.py
from flask import Flask, render_template, jsonify, request
from nucleo import Clima, consenso, generar_proyeccion, map_estado, wmo_to_estado
import requests
import pyodbc
from datetime import datetime

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

# Configuración de APIs 
APIs = [
    {
        "name": "openweather",
        "key": "tu_openweather_key",  # Obtén gratis en openweathermap.org
        "url": "https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric"
    },
    {
        "name": "openmeteo",
        "key": None,
        "url": "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code"
    },
    {
        "name": "weatherapi",
        "key": "tu_weatherapi_key",  # Obtén gratis en weatherapi.com
        "url": "https://api.weatherapi.com/v1/current.json?key={key}&q={lat},{lon}"
    }
]

# Configuración de SQL Server 
DB_CONN_STR = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'  
    'DATABASE=zephyra_db;'
    'UID=sa;'  
    'PWD=190205'  
)

def get_db_connection():
    return pyodbc.connect(DB_CONN_STR)

# Crear tablas si no existen (ejecutar una vez o en init)
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='historical' AND xtype='U')
        CREATE TABLE historical (
            id INT IDENTITY(1,1) PRIMARY KEY,
            fecha DATETIME DEFAULT GETDATE(),
            ciudad VARCHAR(255),
            temperatura FLOAT,
            humedad FLOAT,
            estado VARCHAR(50)
        )
    """)
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='favorites' AND xtype='U')
        CREATE TABLE favorites (
            id INT IDENTITY(1,1) PRIMARY KEY,
            ciudad VARCHAR(255),
            lat FLOAT,
            lon FLOAT
        )
    """)
    conn.commit()
    conn.close()

# Llama a init_db() una vez al iniciar la app
init_db()

def get_weather_from_api(api, lat, lon):
    """Obtiene datos de una API específica."""
    try:
        key = api["key"] or ""
        url = api["url"].format(lat=lat, lon=lon, key=key)
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            return None
        data = res.json()
        
        if api["name"] == "openweather":
            if "main" not in data:
                return None
            estado_text = data["weather"][0]["description"] if data["weather"] else ""
            return {
                "temperatura": data["main"]["temp"],
                "humedad": data["main"]["humidity"],
                "estado": map_estado(estado_text)
            }
        elif api["name"] == "openmeteo":
            current = data.get("current", {})
            if not current:
                return None
            code = current.get("weather_code", 0)
            return {
                "temperatura": current["temperature_2m"],
                "humedad": current["relative_humidity_2m"],
                "estado": wmo_to_estado(code)
            }
        elif api["name"] == "weatherapi":
            current = data.get("current", {})
            if not current:
                return None
            estado_text = current["condition"]["text"] if "condition" in current else ""
            return {
                "temperatura": current["temp_c"],
                "humedad": current["humidity"],
                "estado": map_estado(estado_text)
            }
    except Exception:
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.json or {}
    
    # Caso 1: Búsqueda por texto (ciudad/país)
    if "query" in data and data["query"]:
        query = data["query"].strip()
        # Geocoding con Nominatim
        geo_url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
        headers = {"User-Agent": "Zephyra/1.0"}
        try:
            res = requests.get(geo_url, headers=headers, timeout=5)
            geo_data = res.json()
            if not geo_data:
                return jsonify({"error": "Ubicación no encontrada"}), 404
            lat = float(geo_data[0]["lat"])
            lon = float(geo_data[0]["lon"])
            ciudad = geo_data[0]["display_name"].split(",")[0].strip()
        except Exception as e:
            print(f"Geocoding error: {e}")
            return jsonify({"error": "Error en geocoding"}), 500
    
    # Caso 2: Búsqueda por coordenadas (favoritos)
    elif "lat" in data and "lon" in data:
        lat = float(data["lat"])
        lon = float(data["lon"])
        # Reverse geocoding para obtener nombre de ciudad
        rev_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {"User-Agent": "Zephyra/1.0"}
        try:
            res = requests.get(rev_url, headers=headers, timeout=5)
            rev_data = res.json()
            ciudad = rev_data.get("address", {}).get("city") or \
                     rev_data.get("address", {}).get("town") or \
                     rev_data.get("address", {}).get("village") or \
                     "Ubicación"
        except Exception:
            ciudad = "Ubicación desconocida"
    
    else:
        return jsonify({"error": "Parámetros insuficientes"}), 400
    
    # Obtener lecturas de APIs
    lecturas = []
    for api in APIs:
        lectura = get_weather_from_api(api, lat, lon)
        if lectura:
            lectura["api"] = api["name"]
            lecturas.append(lectura)
    
    # Consenso
    cons = consenso(lecturas, ciudad)
    
    # Proyección (7 días por default)
    dias_proy = data.get("dias", 7)
    proyeccion = generar_proyeccion(cons, dias_proy)
    
    # Guardar en histórico
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO historical (ciudad, temperatura, humedad, estado) VALUES (?, ?, ?, ?)",
            (ciudad, cons.temperatura, cons.humedad, cons.estado)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error guardando en DB: {e}")
    
    return jsonify({
        "lat": lat,
        "lon": lon,
        "ciudad": ciudad,
        "lecturas": lecturas,
        "consenso": cons.__dict__,
        "proyeccion": proyeccion
    })

@app.route("/favorites", methods=["GET", "POST"])
def favorites():
    if request.method == "POST":
        data = request.json
        ciudad = data.get("ciudad")
        lat = data.get("lat")
        lon = data.get("lon")
        if not all([ciudad, lat, lon]):
            return jsonify({"error": "Datos requeridos"}), 400
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO favorites (ciudad, lat, lon) VALUES (?, ?, ?)",
                (ciudad, lat, lon)
            )
            conn.commit()
            conn.close()
            return jsonify({"success": True})
        except Exception as e:
            print(f"Error agregando favorito: {e}")
            return jsonify({"error": "Error en DB"}), 500
    
    # GET: lista de favorites
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ciudad, lat, lon FROM favorites")
        favs = [{"ciudad": row[0], "lat": row[1], "lon": row[2]} for row in cursor.fetchall()]
        conn.close()
        return jsonify(favs)
    except Exception as e:
        print(f"Error obteniendo favorites: {e}")
        return jsonify([])

@app.route("/historical", methods=["GET"])
def historical():
    ciudad = request.args.get("ciudad")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if ciudad:
            cursor.execute("SELECT fecha, temperatura, humedad, estado FROM historical WHERE ciudad = ? ORDER BY fecha DESC", (ciudad,))
        else:
            cursor.execute("SELECT fecha, ciudad, temperatura, humedad, estado FROM historical ORDER BY fecha DESC")
        hist = [{"fecha": row[0].isoformat(), "ciudad": row[1] if not ciudad else ciudad, "temperatura": row[1 if ciudad else 2], "humedad": row[2 if ciudad else 3], "estado": row[3 if ciudad else 4]} for row in cursor.fetchall()]
        conn.close()
        return jsonify(hist)
    except Exception as e:
        print(f"Error obteniendo histórico: {e}")
        return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)