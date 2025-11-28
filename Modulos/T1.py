#Desarrollar módulo de conexión y autenticación a APIs meteorológicas.
from dataclasses import dataclass

@dataclass
class APIConfig:
    name: str
    key: str | None
    url: str

APIS = [
    APIConfig(
        name="openweather",
        key="tu_openweather_key",
        url="https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric"
    ),
    APIConfig(
        name="openmeteo",
        key=None,
        url="https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code"
    ),
    APIConfig(
        name="weatherapi",
        key="tu_weatherapi_key",
        url="https://api.weatherapi.com/v1/current.json?key={key}&q={lat},{lon}"
    )
]

DB_CONN_STR = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=zephyra_db;'
    'UID=sa;'
    'PWD=tu_password'
)
