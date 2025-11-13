from dataclasses import dataclass
from typing import Literal, List, Dict
import random

# Posibles estados climáticos
EstadoClima = Literal["soleado", "nublado", "lluvioso"]

@dataclass(frozen=True)
class Clima:
    dia: int
    ciudad: str
    estado: EstadoClima
    temperatura: float
    humedad: float

def siguiente_clima(actual: Clima) -> Clima:
    """Genera el clima del día siguiente basado en la transición probabilística del estado actual."""
    cambios = {
        "soleado": "nublado" if random.random() < 0.3 else "soleado",
        "nublado": "lluvioso" if random.random() < 0.4 else "soleado",
        "lluvioso": "nublado" if random.random() < 0.5 else "lluvioso",
    }
    nuevo_estado = cambios[actual.estado]
    nueva_temp = max(10, min(40, actual.temperatura + random.uniform(-2, 2)))
    nueva_humedad = max(5, min(100, actual.humedad + random.uniform(-5, 5)))
    return Clima(
        dia=actual.dia + 1,
        ciudad=actual.ciudad,
        estado=nuevo_estado,
        temperatura=nueva_temp,
        humedad=nueva_humedad
    )

def simular_varios(inicial: Clima, dias: int) -> List[Clima]:
    """Simula la evolución del clima durante un número de días consecutivos."""
    lista = [inicial]
    actual = inicial
    for _ in range(dias):
        actual = siguiente_clima(actual)
        lista.append(actual)
    return lista

def filtrar_por_ciudad(datos: List[Clima], ciudad: str) -> List[Clima]:
    """Filtra las lecturas de clima de una ciudad específica."""
    return [c for c in datos if c.ciudad.lower() == ciudad.lower()]

def promedio_ciudad(datos: List[Clima]) -> Dict[str, float]:
    """Calcula el promedio de temperatura y humedad de una lista de registros climáticos."""
    if not datos:
        return {"temperatura": 0, "humedad": 0}
    temp_prom = sum(c.temperatura for c in datos) / len(datos)
    hum_prom = sum(c.humedad for c in datos) / len(datos)
    return {"temperatura": round(temp_prom, 2), "humedad": round(hum_prom, 2)}

def generar_proyeccion(inicial: Clima, dias: int) -> Dict[str, float]:
    """Genera una proyección meteorológica promedio a futuro."""
    simulacion = simular_varios(inicial, dias)
    return promedio_ciudad(simulacion)
