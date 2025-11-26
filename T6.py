# Implementar cálculo automático del índice de confianza.
from typing import List, Dict

def indice_confianza(lecturas: List[Dict]) -> float:
    if len(lecturas) < 2:
        return 0.0
    temps = [l['temperatura'] for l in lecturas if 'temperatura' in l]
    if not temps:
        return 0.0
    varianza = sum((x - sum(temps)/len(temps))**2 for x in temps) / len(temps)
    return round(max(0, 100 - varianza * 10), 2)