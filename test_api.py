# test/test_api.py
import pytest
import requests

BASE_URL = "http://localhost:5000"

def test_api_search_qquito():
    response = requests.post(
        f"{BASE_URL}/search",
        json={"query": "Quito", "dias": 7}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "consenso" in data
    assert "proyeccion" in data
    assert 10 <= data["proyeccion"]["temperatura"] <= 40
    assert 5 <= data["proyeccion"]["humedad"] <= 100