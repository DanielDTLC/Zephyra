# Crear módulo de normalización de datos (formato, unidades, estructura).
from dataclasses import dataclass
from typing import Literal

EstadoClima = Literal["soleado", "nublado", "lluvioso"]

@dataclass(frozen=True)
class Clima:
    dia: int
    ciudad: str
    estado: EstadoClima
    temperatura: float
    humedad: float
