import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app

client = TestClient(app)


class TestAPIWithMocks:
    """Тесты API с моками для базы данных"""

    @patch('main.db_manager.get_mountain_pass')
    def test_get_nonexistent_pass(self, mock_get):
        """Тест получения несуществующего перевала"""
        # Настраиваем мок для возврата None (не найден)
        mock_get.return_value = None

        response = client.get("/submitData/999999")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        # Принимаем оба возможных сообщения
        assert data["detail"] in ["Перевал не найден", "Ресурс не найден"]

    @patch('main.db_manager.get_passes_by_user_email')
    def test_get_passes_by_email_success(self, mock_get):
        """Тест успешного получения перевалов по email"""
        # Настраиваем мок для возврата пустого списка
        mock_get.return_value = []

        response = client.get("/submitData/?user__email=nonexistent@example.com")
        assert response.status_code == 200
        assert response.json() == []

    @patch('main.db_manager.get_passes_by_user_email')
    def test_get_passes_by_email_with_data(self, mock_get):
        """Тест получения перевалов по email с данными"""
        mock_data = [
            {
                "id": 1,
                "title": "Тестовый перевал",
                "latitude": 43.123456,
                "longitude": 42.654321,
                "height": 3500,
                "status": "new",
                "add_time": "2024-01-15T10:30:00",
                "full_name": "Иван Иванов",
                "email": "test@example.com",
                "phone": "+79991234567",
                "photos": []
            }
        ]
        mock_get.return_value = mock_data

        response = client.get("/submitData/?user__email=test@example.com")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['title'] == "Тестовый перевал"

    @patch('main.db_manager.update_mountain_pass')
    def test_update_pass_success(self, mock_update):
        """Тест успешного обновления перевала"""
        mock_update.return_value = {
            'state': 1,
            'message': 'Запись успешно обновлена'
        }

        update_data = {
            "title": "Обновленный перевал",
            "latitude": 44.123456,
            "longitude": 43.654321,
            "height": 3600,
            "user": {
                "email": "test@example.com",
                "full_name": "Иван Иванов",
                "phone": "+79991234567"
            },
            "photos": []
        }

        response = client.patch("/submitData/1", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data['state'] == 1

    @patch('main.db_manager.update_mountain_pass')
    def test_update_pass_failed(self, mock_update):
        """Тест неудачного обновления перевала"""
        mock_update.return_value = {
            'state': 0,
            'message': 'Редактирование возможно только для записей со статусом "new"'
        }

        update_data = {
            "title": "Обновленный перевал",
            "latitude": 44.123456,
            "longitude": 43.654321,
            "height": 3600,
            "user": {
                "email": "test@example.com",
                "full_name": "Иван Иванов",
                "phone": "+79991234567"
            },
            "photos": []
        }

        response = client.patch("/submitData/1", json=update_data)
        assert response.status_code == 400
        data = response.json()
        assert 'Редактирование возможно только' in data['detail']

    @patch('main.db_manager.add_mountain_pass')
    def test_submit_data_success(self, mock_add):
        """Тест успешного добавления перевала"""
        # Настраиваем мок
        mock_add.return_value = {
            'status': 200,
            'message': 'Отправлено успешно',
            'id': 1
        }

        test_data = {
            "title": "Тестовый перевал",
            "latitude": 43.123456,
            "longitude": 42.654321,
            "height": 3500,
            "user": {
                "email": "test@example.com",
                "full_name": "Иван Иванов",
                "phone": "+79991234567"
            },
            "photos": [
                {"url": "https://example.com/photo1.jpg"}
            ]
        }

        response = client.post("/submitData", json=test_data)
        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'Отправлено успешно'
        assert data['id'] == 1

    @patch('main.db_manager.add_mountain_pass')
    def test_submit_data_db_error(self, mock_add):
        """Тест ошибки базы данных при добавлении"""
        mock_add.return_value = {
            'status': 500,
            'message': 'Ошибка при выполнении операции'
        }

        test_data = {
            "title": "Тестовый перевал",
            "latitude": 43.123456,
            "longitude": 42.654321,
            "height": 3500,
            "user": {
                "email": "test@example.com",
                "full_name": "Иван Иванов",
                "phone": "+79991234567"
            }
        }

        response = client.post("/submitData", json=test_data)
        assert response.status_code == 500
        data = response.json()
        assert 'Ошибка при выполнении операции' in data['detail']