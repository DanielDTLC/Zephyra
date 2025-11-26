# Implementar módulo de geolocalización (país/ciudad).
import requests

def geocode_query(query: str):
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
    headers = {"User-Agent": "Zephyra/1.0"}
    res = requests.get(url, headers=headers, timeout=5)
    data = res.json()
    if not data: return None
    return {
        "lat": float(data[0]["lat"]),
        "lon": float(data[0]["lon"]),
        "ciudad": data[0]["display_name"].split(",")[0].strip()
    }

# Integrar la búsqueda con APIs por coordenadas.
def reverse_geocode(lat: float, lon: float):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    headers = {"User-Agent": "Zephyra/1.0"}
    res = requests.get(url, headers=headers, timeout=5)
    data = res.json()
    address = data.get("address", {})
    return address.get("city") or address.get("town") or address.get("village") or "Ubicación"