# app.py
from flask import Flask, render_template, request, jsonify
from T1 import APIS
from T1_2 import get_weather_from_api
from T12_T13 import geocode_query, reverse_geocode
from T3 import save_historical
from T15 import save_favorite, get_favorites
from T5 import consenso
from T7 import generar_proyeccion
from T6 import indice_confianza

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.json or {}
    
    if "query" in data and data["query"]:
        geo = geocode_query(data["query"])
        if not geo: return jsonify({"error": "Ubicación no encontrada"}), 404
        lat, lon, ciudad = geo["lat"], geo["lon"], geo["ciudad"]
    elif "lat" in data and "lon" in data:
        lat, lon = float(data["lat"]), float(data["lon"])
        ciudad = reverse_geocode(lat, lon)
    else:
        return jsonify({"error": "Parámetros insuficientes"}), 400

    lecturas = [l for api in APIS if (l := get_weather_from_api(api, lat, lon))]
    for l in lecturas: l["api"] = next(a.name for a in APIS if a.name == l.get("api", ""))
    
    cons = consenso(lecturas, ciudad)
    proy = generar_proyeccion(cons, data.get("dias", 7))
    conf = indice_confianza(lecturas)
    
    save_historical(ciudad, cons.temperatura, cons.humedad, cons.estado, lat, lon)
    
    return jsonify({
        "lat": lat, "lon": lon, "ciudad": ciudad,
        "lecturas": lecturas, "consenso": cons.__dict__,
        "proyeccion": proy, "confianza": conf
    })

@app.route("/favorites", methods=["GET", "POST"])
def favorites():
    if request.method == "POST":
        data = request.json
        save_favorite(data["ciudad"], data["lat"], data["lon"])
        return jsonify({"success": True})
    return jsonify(get_favorites())

if __name__ == "__main__":
    app.run(debug=True)
