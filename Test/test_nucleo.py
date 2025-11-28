# test/test_nucleo.py
import pytest
from hypothesis import given, strategies as st

# IMPORTS CORRECTOS para tu estructura actual
from nucleo import Clima, siguiente_clima, simular_varios, generar_proyeccion

# -------------------------------------------------
# PRUEBAS UNITARIAS
# -------------------------------------------------

def test_siguiente_clima_transicion_valida():
    # Caso normal
    actual = Clima(dia=1, ciudad="Quito", estado="soleado", temperatura=20.0, humedad=60.0)
    siguiente = siguiente_clima(actual)
    
    assert siguiente.dia == 2
    assert siguiente.ciudad == "Quito"
    assert siguiente.estado in ["soleado", "nublado"]
    assert 10 <= siguiente.temperatura <= 40
    assert 5 <= siguiente.humedad <= 100

def test_generar_proyeccion_cero_dias():
    # Caso borde: 0 días
    inicial = Clima(dia=1, ciudad="Guayaquil", estado="soleado", temperatura=30.0, humedad=80.0)
    proy = generar_proyeccion(inicial, 0)
    
    assert proy["temperatura"] == 30.0
    assert proy["humedad"] == 80.0

# -------------------------------------------------
# PRUEBAS DE PROPIEDADES
# -------------------------------------------------

@given(
    temp=st.floats(min_value=10, max_value=40),
    hum=st.floats(min_value=5, max_value=100)
)
def test_siguiente_clima_rangos_siempre_validos(temp, hum):
    inicial = Clima(1, "Test", "soleado", temp, hum)
    siguiente = siguiente_clima(inicial)
    assert 10 <= siguiente.temperatura <= 40
    assert 5 <= siguiente.humedad <= 100
