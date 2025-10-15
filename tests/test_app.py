import sys
import os

# Добавляем корневую директорию в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from main import app
from tests.mock_database import MockDatabaseManager

# Заменяем реальный DatabaseManager на мок
import main

main.db_manager = MockDatabaseManager()

# Создаем тестового клиента
client = TestClient(app)


def safe_get_json(response, key, default="N/A"):
    """Безопасное получение значения из JSON ответа"""
    try:
        data = response.json()
        return data.get(key, default)
    except:
        return default


def test_full_workflow():
    """
    Полный тест workflow API без реальной базы данных
    """
    print("🚀 Запуск полного теста workflow API...")

    # 1. Тест корневого endpoint
    print("\n1. Тестирование корневого endpoint...")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ Ответ: {data['message']}")

    # 2. Тест health check
    print("\n2. Тестирование health check...")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ Статус: {data['status']}, База данных: {data['database']}")

    # 3. Тест добавления перевала
    print("\n3. Тестирование добавления перевала...")
    test_data = {
        "title": "Перевал Дятлова",
        "latitude": 61.750312,
        "longitude": 59.465139,
        "height": 1079,
        "user": {
            "email": "ivan.petrov@example.com",
            "full_name": "Петров Иван Сергеевич",
            "phone": "+79123456789"
        },
        "photos": [
            {
                "url": "https://example.com/photo1.jpg"
            },
            {
                "data": "base64_encoded_image_data_here"
            }
        ]
    }

    response = client.post("/submitData", json=test_data)
    assert response.status_code == 200
    data = response.json()
    pass_id = data['id']
    print(f"   ✅ Перевал добавлен с ID: {pass_id}")

    # 4. Тест получения добавленного перевала
    print(f"\n4. Тестирование получения перевала ID: {pass_id}...")
    response = client.get(f"/submitData/{pass_id}")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ Получен перевал: {data['title']}")
    print(f"   ✅ Статус: {data['status']}")
    print(f"   ✅ Пользователь: {safe_get_json(response, 'full_name')}")
    print(f"   ✅ Email: {safe_get_json(response, 'email')}")
    print(f"   ✅ Телефон: {safe_get_json(response, 'phone')}")

    # 5. Тест обновления перевала
    print(f"\n5. Тестирование обновления перевала ID: {pass_id}...")
    update_data = {
        "title": "Перевал Дятлова (уточнено)",
        "latitude": 61.750500,
        "longitude": 59.465200,
        "height": 1080,
        "user": {
            "email": "ivan.petrov@example.com",
            "full_name": "Петров Иван Сергеевич",
            "phone": "+79123456789"
        },
        "photos": [
            {
                "url": "https://example.com/updated_photo.jpg"
            }
        ]
    }

    response = client.patch(f"/submitData/{pass_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ Перевал обновлен: {data['message']}")

    # 6. Проверяем, что данные обновились
    response = client.get(f"/submitData/{pass_id}")
    assert response.status_code == 200
    updated_data = response.json()
    print(f"   ✅ Новое название: {updated_data['title']}")
    print(f"   ✅ Новая высота: {updated_data['height']}м")

    # 7. Тест получения перевалов пользователя
    print("\n7. Тестирование получения перевалов пользователя...")
    response = client.get("/submitData/?user__email=ivan.petrov@example.com")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ Найдено перевалов: {len(data)}")
    if data:
        print(f"   ✅ Первый перевал: {data[0]['title']}")
        print(f"   ✅ Email пользователя: {data[0].get('email', 'N/A')}")

    # 8. Тест получения несуществующего перевала
    print("\n8. Тестирование получения несуществующего перевала...")
    response = client.get("/submitData/999999")
    assert response.status_code == 404
    error_detail = safe_get_json(response, 'detail', 'Ошибка не указана')
    print(f"   ✅ Корректно обработано: {error_detail}")

    # 9. Тест валидации данных
    print("\n9. Тестирование валидации данных...")
    invalid_data = {
        "title": "Т",  # Слишком короткое
        "latitude": 100,  # Невалидная широта
        "longitude": 200,  # Невалидная долгота
        "height": -100,  # Отрицательная высота
        "user": {
            "email": "invalid-email",
            "full_name": "И",
            "phone": "1"
        }
    }

    response = client.post("/submitData", json=invalid_data)
    assert response.status_code == 422
    print(f"   ✅ Валидация работает: {response.status_code}")

    # 10. Тест информации о сервисе
    print("\n10. Тестирование информации о сервисе...")
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ Сервис: {data['service']}")
    print(f"   ✅ Версия: {data['version']}")

    print("\n🎉 Все тесты пройдены успешно! API работает без реальной базы данных.")


if __name__ == "__main__":
    test_full_workflow()