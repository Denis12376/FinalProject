#!/usr/bin/env python3
"""
Скрипт для быстрой проверки API без базы данных
"""

import sys
import os

# Добавляем корневую директорию в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from main import app
from tests.mock_database import MockDatabaseManager

# Настраиваем мок
import main

main.db_manager = MockDatabaseManager()

client = TestClient(app)


def safe_get(response, key, default="N/A"):
    """Безопасное получение данных из ответа"""
    try:
        data = response.json()
        return data.get(key, default)
    except:
        return default


def check_api():
    """Проверка всех основных функций API"""
    print("🔍 Проверка Mountain Passes API (тестовый режим)...")

    checks_passed = 0
    checks_failed = 0

    try:
        # 1. Проверка основных endpoints
        print("\n1. Проверка основных endpoints...")
        endpoints = [
            ("GET", "/", "Корневой endpoint"),
            ("GET", "/health", "Health check"),
            ("GET", "/info", "Информация о сервисе"),
        ]

        for method, endpoint, description in endpoints:
            print(f"   🔍 {description}...")
            if method == "GET":
                response = client.get(endpoint)
                if response.status_code == 200:
                    print(f"      ✅ Работает")
                    checks_passed += 1
                else:
                    print(f"      ❌ Ошибка: {response.status_code}")
                    checks_failed += 1

        # 2. Тест добавления данных
        print("\n2. Тестирование добавления перевала...")
        test_data = {
            "title": "Тестовый перевал для проверки",
            "latitude": 43.123456,
            "longitude": 42.654321,
            "height": 3500,
            "user": {
                "email": "check@example.com",
                "full_name": "Тестовый Пользователь",
                "phone": "+79991234567"
            },
            "photos": [
                {"url": "https://example.com/test_photo.jpg"}
            ]
        }

        response = client.post("/submitData", json=test_data)
        if response.status_code == 200:
            pass_id = safe_get(response, 'id')
            print(f"   ✅ Добавлен перевал ID: {pass_id}")
            checks_passed += 1

            # Проверяем получение
            response = client.get(f"/submitData/{pass_id}")
            if response.status_code == 200:
                print(f"   ✅ Получен перевал: {safe_get(response, 'title')}")
                checks_passed += 1
            else:
                print(f"   ❌ Ошибка получения: {response.status_code}")
                checks_failed += 1
        else:
            print(f"   ❌ Ошибка добавления: {response.status_code}")
            checks_failed += 1

        # 3. Проверка поиска по email
        print(f"\n3. Поиск перевалов пользователя...")
        response = client.get("/submitData/?user__email=check@example.com")
        if response.status_code == 200:
            passes = response.json()
            print(f"   ✅ Найдено перевалов: {len(passes)}")
            checks_passed += 1
        else:
            print(f"   ❌ Ошибка поиска: {response.status_code}")
            checks_failed += 1

        # 4. Проверка обработки ошибок
        print(f"\n4. Проверка обработки ошибок...")
        response = client.get("/submitData/999999")
        if response.status_code == 404:
            error_msg = safe_get(response, 'detail', 'Ошибка не указана')
            print(f"   ✅ 404 ошибка обработана: {error_msg}")
            checks_passed += 1
        else:
            print(f"   ❌ Неправильная обработка 404: {response.status_code}")
            checks_failed += 1

        # 5. Проверка документации
        print(f"\n5. Проверка документации...")
        response = client.get("/docs")
        if response.status_code == 200:
            print(f"   ✅ Swagger документация доступна")
            checks_passed += 1
        else:
            print(f"   ❌ Документация недоступна: {response.status_code}")
            checks_failed += 1

        # Итоги
        print(f"\n📊 ИТОГИ ПРОВЕРКИ:")
        print(f"✅ Пройдено: {checks_passed}")
        print(f"❌ Ошибок: {checks_failed}")

        if checks_failed == 0:
            print("\n🎉 Все проверки пройдены! API работает корректно.")
        else:
            print("\n⚠️  Некоторые проверки не пройдены.")

    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        checks_failed += 1

if __name__ == "__main__":
    check_api()