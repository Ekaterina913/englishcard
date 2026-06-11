import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()


class Database:
    def __init__(self):
        # Берём параметры из переменных окружения
        self.conn_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', 5432),
            'dbname': os.getenv('DB_NAME', 'englishcard'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }

    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(**self.conn_params)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        """Инициализация базы данных и заполнение начальными словами"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Создание таблиц
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS base_words (
                        id SERIAL PRIMARY KEY,
                        word_ru VARCHAR(100) NOT NULL,
                        word_en VARCHAR(100) NOT NULL,
                        category VARCHAR(50)
                    )
                ''')
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS user_words (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        word_ru VARCHAR(100) NOT NULL,
                        word_en VARCHAR(100) NOT NULL,
                        correct_answers INTEGER DEFAULT 0,
                        total_attempts INTEGER DEFAULT 0,
                        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, word_ru)
                    )
                ''')

                # Заполнение базовыми словами (10 слов)
                base_words = [
                    ('я', 'I', 'pronouns'),
                    ('ты', 'you', 'pronouns'),
                    ('он', 'he', 'pronouns'),
                    ('она', 'she', 'pronouns'),
                    ('оно', 'it', 'pronouns'),
                    ('мы', 'we', 'pronouns'),
                    ('они', 'they', 'pronouns'),
                    ('красный', 'red', 'colors'),
                    ('синий', 'blue', 'colors'),
                    ('зеленый', 'green', 'colors'),
                ]

                for word_ru, word_en, category in base_words:
                    cur.execute('''
                        INSERT INTO base_words (word_ru, word_en, category)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING
                    ''', (word_ru, word_en, category))

    def get_or_create_user(self, username):
        """Получение или создание пользователя"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute('SELECT * FROM users WHERE username = %s', (username,))
                user = cur.fetchone()
                if not user:
                    cur.execute('INSERT INTO users (username) VALUES (%s) RETURNING *', (username,))
                    user = cur.fetchone()

                    # Добавляем базовые слова для нового пользователя
                    cur.execute('SELECT * FROM base_words')
                    base_words = cur.fetchall()
                    for word in base_words:
                        cur.execute('''
                            INSERT INTO user_words (user_id, word_ru, word_en)
                            VALUES (%s, %s, %s)
                            ON CONFLICT DO NOTHING
                        ''', (user['id'], word['word_ru'], word['word_en']))
                return user

    def get_user_words(self, user_id):
        """Получение всех слов пользователя"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute('SELECT * FROM user_words WHERE user_id = %s', (user_id,))
                return cur.fetchall()

    def add_word(self, user_id, word_ru, word_en):
        """Добавление нового слова для пользователя"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO user_words (user_id, word_ru, word_en)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id, word_ru) DO UPDATE
                    SET word_en = EXCLUDED.word_en
                ''', (user_id, word_ru.lower(), word_en.lower()))
                return True

    def delete_word(self, user_id, word_ru):
        """Удаление слова у пользователя"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    DELETE FROM user_words 
                    WHERE user_id = %s AND word_ru = %s
                ''', (user_id, word_ru))
                return cur.rowcount > 0

    def update_statistics(self, user_id, word_ru, is_correct):
        """Обновление статистики ответов"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    UPDATE user_words 
                    SET total_attempts = total_attempts + 1,
                        correct_answers = correct_answers + %s
                    WHERE user_id = %s AND word_ru = %s
                ''', (1 if is_correct else 0, user_id, word_ru))

    def get_statistics(self, user_id):
        """Получение статистики пользователя"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute('''
                    SELECT COUNT(*) as total_words,
                           SUM(correct_answers) as total_correct,
                           SUM(total_attempts) as total_attempts
                    FROM user_words
                    WHERE user_id = %s
                ''', (user_id,))
                stats = cur.fetchone()
                return stats