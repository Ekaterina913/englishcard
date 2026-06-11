# EnglishCard - Приложение для изучения английского языка

## 📝 Описание
EnglishCard - это веб-приложение для изучения английских слов методом карточек. Пользователь видит русское слово и выбирает правильный перевод из 4 вариантов. Приложение ведёт статистику правильных ответов и позволяет пополнять личный словарь.

## 🚀 Функциональность
- 📖 **Изучение слов** - выбор правильного перевода из 4 вариантов
- ➕ **Добавление слов** - пополнение личного словаря
- 🗑️ **Удаление слов** - удаление ненужных слов из словаря
- 📊 **Статистика** - отслеживание прогресса (правильные ответы, точность)
- 👥 **Персональные словари** - у каждого пользователя свой набор слов

## 🛠️ Технологии
- Python 3.12+
- Streamlit - веб-интерфейс
- PostgreSQL - база данных
- psycopg2 - драйвер для работы с PostgreSQL
- python-dotenv - управление переменными окружения

## 📊 Структура базы данных

### Таблица users
| Колонка | Тип | Описание |
|---------|-----|----------|
| id | SERIAL | PRIMARY KEY |
| username | VARCHAR(100) | Имя пользователя |
| created_at | TIMESTAMP | Дата регистрации |

### Таблица base_words
| Колонка | Тип | Описание |
|---------|-----|----------|
| id | SERIAL | PRIMARY KEY |
| word_ru | VARCHAR(100) | Слово на русском |
| word_en | VARCHAR(100) | Перевод на английский |
| category | VARCHAR(50) | Категория слова |

### Таблица user_words
| Колонка | Тип | Описание |
|---------|-----|----------|
| id | SERIAL | PRIMARY KEY |
| user_id | INTEGER | FOREIGN KEY → users(id) |
| word_ru | VARCHAR(100) | Слово на русском |
| word_en | VARCHAR(100) | Перевод на английский |
| correct_answers | INTEGER | Количество правильных ответов |
| total_attempts | INTEGER | Всего попыток |
| added_at | TIMESTAMP | Дата добавления |

## 📦 Установка и запуск

### Требования
- Python 3.12 или выше
- PostgreSQL 15 или выше
- Git

### Шаг 1: Клонирование репозитория
```bash
git clone https://github.com/ВАШ_НИК/englishcard.git
cd englishcard
```

Шаг 2: Создание виртуального окружения

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

Шаг 4: Настройка базы данных PostgreSQL

1. Запустите PgAdmin
2. Создайте базу данных:

```sql
CREATE DATABASE englishcard;
```

3. Создайте файл .env в корне проекта:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=englishcard
DB_USER=postgres
DB_PASSWORD=ВАШ_ПАРОЛЬ
```

Шаг 5: Инициализация базы данных

```bash
python -c "from database import Database; db = Database(); db.init_db()"
```

Шаг 6: Запуск приложения

```bash
streamlit run main.py
```

После запуска откройте в браузере: http://localhost:8501