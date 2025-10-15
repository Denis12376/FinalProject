from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MockDatabaseManager:
    """
    Мок-класс для тестирования без реальной базы данных
    """

    def __init__(self):
        self.passes_data = {}
        self.next_id = 1
        self.users_data = {}
        logger.info("Инициализирован MockDatabaseManager")

    def get_connection(self):
        """Мок метода соединения с БД"""
        return type('MockConnection', (), {'close': lambda: None})()

    def add_mountain_pass(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Мок метода добавления перевала
        """
        try:
            logger.info(f"Мок: добавление перевала '{data['title']}'")

            # Проверяем обязательные поля
            required_fields = ['title', 'latitude', 'longitude', 'height', 'user']
            for field in required_fields:
                if field not in data:
                    return {
                        'status': 400,
                        'message': f'Отсутствует обязательное поле: {field}'
                    }

            # Сохраняем пользователя
            user_email = data['user']['email']
            self.users_data[user_email] = data['user']

            # Сохраняем перевал
            pass_id = self.next_id
            current_time = datetime.now().isoformat()

            self.passes_data[pass_id] = {
                'id': pass_id,
                'title': data['title'],
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'height': data['height'],
                'status': 'new',
                'add_time': current_time,
                'user_email': user_email,
                'photos': data.get('photos', [])
            }

            self.next_id += 1

            return {
                'status': 200,
                'message': 'Отправлено успешно',
                'id': pass_id
            }

        except Exception as e:
            logger.error(f"Мок: ошибка при добавлении: {str(e)}")
            return {
                'status': 500,
                'message': f'Ошибка при выполнении операции: {str(e)}'
            }

    def get_mountain_pass(self, pass_id: int) -> Optional[Dict[str, Any]]:
        """
        Мок метода получения перевала по ID
        """
        try:
            logger.info(f"Мок: получение перевала ID: {pass_id}")

            if pass_id in self.passes_data:
                pass_data = self.passes_data[pass_id].copy()
                user_email = pass_data.pop('user_email')
                user_data = self.users_data.get(user_email, {})

                # Формируем правильную структуру ответа
                result = {
                    'id': pass_data['id'],
                    'title': pass_data['title'],
                    'latitude': float(pass_data['latitude']),
                    'longitude': float(pass_data['longitude']),
                    'height': pass_data['height'],
                    'status': pass_data['status'],
                    'add_time': pass_data['add_time'],
                    'full_name': user_data.get('full_name', ''),
                    'email': user_email,
                    'phone': user_data.get('phone', ''),
                    'photos': pass_data.get('photos', [])
                }
                return result
            else:
                return None

        except Exception as e:
            logger.error(f"Мок: ошибка при получении: {str(e)}")
            return None

    def update_mountain_pass(self, pass_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Мок метода обновления перевала
        """
        try:
            logger.info(f"Мок: обновление перевала ID: {pass_id}")

            if pass_id not in self.passes_data:
                return {'state': 0, 'message': 'Запись не найдена'}

            if self.passes_data[pass_id]['status'] != 'new':
                return {'state': 0, 'message': 'Редактирование возможно только для записей со статусом "new"'}

            # Обновляем данные
            self.passes_data[pass_id].update({
                'title': data['title'],
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'height': data['height'],
                'photos': data.get('photos', [])
            })

            return {
                'state': 1,
                'message': 'Запись успешно обновлена'
            }

        except Exception as e:
            logger.error(f"Мок: ошибка при обновлении: {str(e)}")
            return {
                'state': 0,
                'message': f'Ошибка при обновлении: {str(e)}'
            }

    def get_passes_by_user_email(self, email: str) -> List[Dict[str, Any]]:
        """
        Мок метода получения перевалов по email пользователя
        """
        try:
            logger.info(f"Мок: получение перевалов пользователя: {email}")

            result = []
            user_data = self.users_data.get(email, {})

            for pass_id, pass_data in self.passes_data.items():
                if pass_data['user_email'] == email:
                    result.append({
                        'id': pass_data['id'],
                        'title': pass_data['title'],
                        'latitude': float(pass_data['latitude']),
                        'longitude': float(pass_data['longitude']),
                        'height': pass_data['height'],
                        'status': pass_data['status'],
                        'add_time': pass_data['add_time'],
                        'full_name': user_data.get('full_name', ''),
                        'email': email,
                        'phone': user_data.get('phone', ''),
                        'photos': pass_data.get('photos', [])
                    })

            return result

        except Exception as e:
            logger.error(f"Мок: ошибка при получении по email: {str(e)}")
            return []