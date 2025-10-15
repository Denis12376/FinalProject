import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
import sys
import os




sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from tests.mock_database import MockDatabaseManager

# Создаем тестового клиента
client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_database():
    """Фикстура для автоматической замены базы данных на мок"""
    with patch('main.db_manager', MockDatabaseManager()):
        yield


class TestAPIWithMock:
    """Тесты API с моком базы данных"""

    def test_full_workflow(self):
        """Полный тест workflow с моком"""
        # 1. Добавление перевала
        test_data = {
            "title": "Тестовый перевал",
            "latitude": 43.123456,
            "longitude": 42.654321,
            "height": 3500,
            "user": {
                "email": "test@example.com",
                "full_name": "Тестовый Пользователь",
                "phone": "+79991234567"
            },
            "photos": [
                {"url": "https://example.com/photo1.jpg"}
            ]
        }

        response = client.post("/submitData", json=test_data)
        assert response.status_code == 200
        data = response.json()
        pass_id = data['id']

        # 2. Получение перевала
        response = client.get(f"/submitData/{pass_id}")
        assert response.status_code == 200
        data = response.json()
        assert data['title'] == "Тестовый перевал"
        assert data['status'] == 'new'

        # 3. Обновление перевала
        update_data = {
            "title": "Обновленный перевал",
            "latitude": 44.123456,
            "longitude": 43.654321,
            "height": 3600,
            "user": {
                "email": "test@example.com",
                "full_name": "Тестовый Пользователь",
                "phone": "+79991234567"
            },
            "photos": []
        }

        response = client.patch(f"/submitData/{pass_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data['state'] == 1

        # 4. Получение перевалов пользователя
        response = client.get("/submitData/?user__email=test@example.com")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['title'] == "Обновленный перевал"

    def test_get_nonexistent_pass(self):
        """Тест получения несуществующего перевала"""
        response = client.get("/submitData/999999")
        assert response.status_code == 404
        data = response.json()
        # Принимаем оба возможных сообщения
        assert data['detail'] in ["Перевал не найден", "Ресурс не найден"]

    def test_validation_errors(self):
        """Тест ошибок валидации"""
        # Невалидные данные
        invalid_data = {
            "title": "Т",
            "latitude": 1000,
            "longitude": 2000,
            "height": -100,
            "user": {
                "email": "invalid",
                "full_name": "И",
                "phone": "1"
            }
        }

        response = client.post("/submitData", json=invalid_data)
        assert response.status_code == 422

    def test_service_endpoints(self):
        """Тест сервисных endpoints"""
        response = client.get("/")
        assert response.status_code == 200

        response = client.get("/health")
        assert response.status_code == 200

        response = client.get("/info")
        assert response.status_code == 200