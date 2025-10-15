import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, List, Optional


class DatabaseManager:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('FSTR_DB_HOST', 'localhost'),
            'port': os.getenv('FSTR_DB_PORT', '5432'),
            'login': os.getenv('FSTR_DB_LOGIN', 'postgres'),
            'password': os.getenv('FSTR_DB_PASS', 'password'),
            'database': os.getenv('FSTR_DB_NAME', 'mountain_passes_db')
        }

    def get_connection(self):
        """Создает соединение с базой данных"""
        return psycopg2.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            user=self.db_config['login'],
            password=self.db_config['password'],
            database=self.db_config['database']
        )

    def add_mountain_pass(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Добавляет информацию о перевале в базу данных
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Проверяем обязательные поля
                required_fields = ['title', 'latitude', 'longitude', 'height', 'user']
                for field in required_fields:
                    if field not in data:
                        return {
                            'status': 400,
                            'message': f'Отсутствует обязательное поле: {field}'
                        }

                # Сначала добавляем/получаем пользователя
                cursor.execute("""
                    INSERT INTO users (email, full_name, phone) 
                    VALUES (%s, %s, %s)
                    ON CONFLICT (email) DO UPDATE SET
                    full_name = EXCLUDED.full_name,
                    phone = EXCLUDED.phone
                    RETURNING id
                """, (data['user']['email'], data['user']['full_name'], data['user']['phone']))

                user_id = cursor.fetchone()['id']

                # Добавляем перевал
                cursor.execute("""
                    INSERT INTO mountain_passes 
                    (user_id, title, latitude, longitude, height, status) 
                    VALUES (%s, %s, %s, %s, %s, 'new')
                    RETURNING id
                """, (user_id, data['title'], data['latitude'],
                      data['longitude'], data['height']))

                pass_id = cursor.fetchone()['id']

                # Добавляем фотографии
                for photo in data.get('photos', []):
                    cursor.execute("""
                        INSERT INTO photos (pass_id, photo_data, photo_url) 
                        VALUES (%s, %s, %s)
                    """, (pass_id, photo.get('data'), photo.get('url')))

                conn.commit()

                return {
                    'status': 200,
                    'message': 'Отправлено успешно',
                    'id': pass_id
                }

        except Exception as e:
            conn.rollback()
            return {
                'status': 500,
                'message': f'Ошибка при выполнении операции: {str(e)}'
            }
        finally:
            conn.close()

    def get_mountain_pass(self, pass_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о перевале по ID
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        mp.id, mp.title, mp.latitude, mp.longitude, 
                        mp.height, mp.status, mp.add_time,
                        u.full_name, u.email, u.phone
                    FROM mountain_passes mp
                    JOIN users u ON mp.user_id = u.id
                    WHERE mp.id = %s
                """, (pass_id,))

                pass_data = cursor.fetchone()
                if not pass_data:
                    return None

                # Получаем фотографии
                cursor.execute("""
                    SELECT photo_data, photo_url 
                    FROM photos 
                    WHERE pass_id = %s
                """, (pass_id,))

                photos = cursor.fetchall()

                result = dict(pass_data)
                result['photos'] = [dict(photo) for photo in photos]

                return result

        except Exception as e:
            return None
        finally:
            conn.close()

    def update_mountain_pass(self, pass_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обновляет информацию о перевале
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Проверяем существование перевала и его статус
                cursor.execute("SELECT status FROM mountain_passes WHERE id = %s", (pass_id,))
                pass_status = cursor.fetchone()

                if not pass_status:
                    return {'state': 0, 'message': 'Запись не найдена'}

                if pass_status['status'] != 'new':
                    return {'state': 0, 'message': 'Редактирование возможно только для записей со статусом "new"'}

                # Обновляем данные перевала
                cursor.execute("""
                    UPDATE mountain_passes 
                    SET title = %s, latitude = %s, longitude = %s, height = %s
                    WHERE id = %s
                """, (data['title'], data['latitude'], data['longitude'],
                      data['height'], pass_id))

                # Обновляем фотографии (удаляем старые, добавляем новые)
                cursor.execute("DELETE FROM photos WHERE pass_id = %s", (pass_id,))

                for photo in data.get('photos', []):
                    cursor.execute("""
                        INSERT INTO photos (pass_id, photo_data, photo_url) 
                        VALUES (%s, %s, %s)
                    """, (pass_id, photo.get('data'), photo.get('url')))

                conn.commit()

                return {
                    'state': 1,
                    'message': 'Запись успешно обновлена'
                }

        except Exception as e:
            conn.rollback()
            return {
                'state': 0,
                'message': f'Ошибка при обновлении: {str(e)}'
            }
        finally:
            conn.close()

    def get_passes_by_user_email(self, email: str) -> List[Dict[str, Any]]:
        """
        Получает все перевалы, добавленные пользователем с указанной почтой
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        mp.id, mp.title, mp.latitude, mp.longitude, 
                        mp.height, mp.status, mp.add_time,
                        u.full_name, u.email, u.phone
                    FROM mountain_passes mp
                    JOIN users u ON mp.user_id = u.id
                    WHERE u.email = %s
                    ORDER BY mp.add_time DESC
                """, (email,))

                passes = cursor.fetchall()
                result = []

                for pass_data in passes:
                    pass_dict = dict(pass_data)

                    # Получаем фотографии для каждого перевала
                    cursor.execute("""
                        SELECT photo_data, photo_url 
                        FROM photos 
                        WHERE pass_id = %s
                    """, (pass_dict['id'],))

                    photos = cursor.fetchall()
                    pass_dict['photos'] = [dict(photo) for photo in photos]
                    result.append(pass_dict)

                return result

        except Exception as e:
            return []
        finally:
            conn.close()