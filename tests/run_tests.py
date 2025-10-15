#!/usr/bin/env python3
"""
Скрипт для запуска всех тестов
"""

import subprocess
import sys
import os


def run_tests():
    print("🚀 Запуск тестов Mountain Passes API...")

    # Запускаем базовые тесты
    print("\n📋 Запуск базовых тестов...")
    result1 = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/test_basic.py", "-v"
    ], capture_output=True, text=True)

    print(result1.stdout)
    if result1.stderr:
        print("STDERR:", result1.stderr)

    # Запускаем тесты с моками
    print("\n📋 Запуск тестов с моками...")
    result2 = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/test_api_with_mocks.py", "tests/test_with_mock.py", "-v"
    ], capture_output=True, text=True)

    print(result2.stdout)
    if result2.stderr:
        print("STDERR:", result2.stderr)

    # Итоги
    print("\n📊 ИТОГИ ТЕСТИРОВАНИЯ:")
    print(f"Базовые тесты: {'✅ ПРОЙДЕНЫ' if result1.returncode == 0 else '❌ ОШИБКИ'}")
    print(f"Тесты с моками: {'✅ ПРОЙДЕНЫ' if result2.returncode == 0 else '❌ ОШИБКИ'}")

    if result1.returncode == 0 and result2.returncode == 0:
        print("\n🎉 Все тесты пройдены успешно!")
        return 0
    else:
        print("\n💥 Некоторые тесты не пройдены")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())