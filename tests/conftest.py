import pytest
import sys
import os
from unittest.mock import patch

# Добавляем корневую директорию в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tests.mock_database import MockDatabaseManager

@pytest.fixture(autouse=True)
def mock_database():
    """Фикстура для автоматической замены базы данных на мок"""
    with patch('main.db_manager', MockDatabaseManager()):
        yield