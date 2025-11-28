# Desarrollar módulo de conexión y autenticación a APIs meteorológicas.
import requests
from T1 import APIS
from T2 import EstadoClima

def map_estado(text: str) -> EstadoClima:
    text_lower = text.lower()
    if "sun" in text_lower or "clear" in text_lower: return "soleado"
    if "cloud" in text_lower or "overcast" in text_lower: return "nublado"
    return "lluvioso"

def wmo_to_estado(code: int) -> EstadoClima:
    if code == 0: return "soleado"
    if 1 <= code <= 3: return "nublado"
    if code >= 51: return "lluvioso"
    return "nublado"

def get_weather_from_api(api, lat, lon):
    try:
        key = api.key or ""
        url = api.url.format(lat=lat, lon=lon, key=key)
        res = requests.get(url, timeout=5)
        if res.status_code != 200: return None
        data = res.json()
        
        if api.name == "openweather":
            estado_text = data["weather"][0]["description"] if data["weather"] else ""
            return {
                "temperatura": data["main"]["temp"],
                "humedad": data["main"]["humidity"],
                "estado": map_estado(estado_text)
            }
        elif api.name == "openmeteo":
            current = data.get("current", {})
            return {
                "temperatura": current["temperature_2m"],
                "humedad": current["relative_humidity_2m"],
                "estado": wmo_to_estado(current.get("weather_code", 0))
            }
        elif api.name == "weatherapi":
            current = data.get("current", {})
            estado_text = current["condition"]["text"] if "condition" in current else ""
            return {
                "temperatura": current["temp_c"],
                "humedad": current["humidity"],
                "estado": map_estado(estado_text)
            }
    except: return None
