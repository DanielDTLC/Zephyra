# Programar el generador de proyecciones climáticas (nucleo.py).
import random
from typing import List, Dict
from T2 import Clima

def siguiente_clima(actual: Clima) -> Clima:
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
    lista = [inicial]
    actual = inicial
    for _ in range(dias):
        actual = siguiente_clima(actual)
        lista.append(actual)
    return lista

def generar_proyeccion(inicial: Clima, dias: int) -> Dict[str, float]:
    simulacion = simular_varios(inicial, dias)
    temp_prom = sum(c.temperatura for c in simulacion) / len(simulacion)
    hum_prom = sum(c.humedad for c in simulacion) / len(simulacion)
    return {"temperatura": round(temp_prom, 2), "humedad": round(hum_prom, 2)}
