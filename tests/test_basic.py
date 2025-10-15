import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app

client = TestClient(app)


class TestBasicEndpoints:
    """Базовые тесты без зависимости от базы данных"""

    def test_root(self):
        """Тест корневого endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_health(self):
        """Тест health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_info(self):
        """Тест информации о сервисе"""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "Mountain Passes API" in data["service"]

    def test_nonexistent_endpoint(self):
        """Тест несуществующего endpoint"""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_validation_error(self):
        """Тест ошибки валидации"""
        invalid_data = {
            "title": "T",  # Слишком короткое
            "latitude": 1000,  # Невалидная широта
            "longitude": 2000,  # Невалидная долгота
            "height": -100,  # Отрицательная высота
            "user": {
                "email": "invalid",
                "full_name": "I",
                "phone": "1"
            }
        }
        response = client.post("/submitData", json=invalid_data)
        assert response.status_code == 422  # Validation error

def test_swagger_docs():
    """Тест доступности документации"""
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/redoc")
    assert response.status_code == 200

    response = client.get("/openapi.json")
    assert response.status_code == 200