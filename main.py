import streamlit as st
import random
from database import Database
import pandas as pd
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Инициализация базы данных
db = Database()

# Инициализация сессии
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'current_word' not in st.session_state:
    st.session_state.current_word = None
if 'options' not in st.session_state:
    st.session_state.options = []
if 'feedback' not in st.session_state:
    st.session_state.feedback = None

# Настройка страницы
st.set_page_config(page_title="EnglishCard", page_icon="📚", layout="wide")

# Боковая панель для входа
with st.sidebar:
    st.title("📚 EnglishCard")
    st.markdown("---")

    if st.session_state.user_id is None:
        username = st.text_input("👤 Введите ваше имя")
        if st.button("Войти"):
            if username:
                user = db.get_or_create_user(username)
                st.session_state.user_id = user['id']
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Пожалуйста, введите имя")
    else:
        st.success(f"Вы вошли как {st.session_state.username}")
        if st.button("Выйти"):
            st.session_state.clear()
            st.rerun()

    st.markdown("---")
    st.caption("Изучай английский с удовольствием!")

# Основной контент (только после входа)
if st.session_state.user_id:
    # Навигация
    menu = st.tabs(["📖 Изучение", "➕ Добавить слово", "🗑️ Удалить слово", "📊 Статистика"])

    # Вкладка "Изучение"
    with menu[0]:
        st.header("Изучаем слова")

        # Получаем слова пользователя
        words = db.get_user_words(st.session_state.user_id)

        if words:
            # Инициализация или получение следующего слова
            if st.session_state.current_word is None:
                current_word = random.choice(words)
                st.session_state.current_word = current_word

                # Генерация вариантов ответов
                other_words = [w for w in words if w['word_en'] != current_word['word_en']]
                options = [current_word['word_en']]
                if len(other_words) >= 3:
                    options.extend([random.choice(other_words)['word_en'] for _ in range(3)])
                else:
                    # Если мало слов, добавляем базовые варианты
                    default_options = ['I', 'you', 'he', 'she', 'it', 'we', 'they']
                    needed = 3 - len(other_words)
                    options.extend(default_options[:needed])
                random.shuffle(options)
                st.session_state.options = options

            # Отображение текущего слова
            st.markdown(f"### Слово: **{st.session_state.current_word['word_ru']}**")
            st.markdown("#### Как будет по-английски?")

            # Отображение кнопок вариантов ответа
            cols = st.columns(2)
            for i, option in enumerate(st.session_state.options):
                with cols[i % 2]:
                    if st.button(option, key=f"btn_{option}_{i}", use_container_width=True):
                        if option == st.session_state.current_word['word_en']:
                            st.session_state.feedback = "✅ Правильно! Отлично!"
                            db.update_statistics(st.session_state.user_id,
                                                 st.session_state.current_word['word_ru'],
                                                 True)
                            st.session_state.current_word = None
                            st.rerun()
                        else:
                            st.session_state.feedback = "❌ Неправильно. Попробуйте еще раз!"
                            db.update_statistics(st.session_state.user_id,
                                                 st.session_state.current_word['word_ru'],
                                                 False)
                            st.rerun()

            # Отображение обратной связи
            if st.session_state.feedback:
                if "✅" in st.session_state.feedback:
                    st.success(st.session_state.feedback)
                else:
                    st.error(st.session_state.feedback)

            # Кнопка пропуска
            if st.button("Следующее слово", type="secondary"):
                st.session_state.current_word = None
                st.session_state.feedback = None
                st.rerun()
        else:
            st.warning("У вас пока нет слов для изучения. Добавьте слова во вкладке 'Добавить слово'")

    # Вкладка "Добавить слово"
    with menu[1]:
        st.header("Добавить новое слово")

        col1, col2 = st.columns(2)
        with col1:
            word_ru = st.text_input("Слово по-русски:")
        with col2:
            word_en = st.text_input("Перевод на английский:")

        if st.button("Добавить слово", type="primary"):
            if word_ru and word_en:
                db.add_word(st.session_state.user_id, word_ru, word_en)
                words_count = len(db.get_user_words(st.session_state.user_id))
                st.success(f"✅ Слово '{word_ru} → {word_en}' добавлено!")
                st.info(f"📊 Теперь вы изучаете {words_count} слов")
                st.balloons()
            else:
                st.error("Пожалуйста, заполните оба поля")

    # Вкладка "Удалить слово"
    with menu[2]:
        st.header("Удалить слово")

        words = db.get_user_words(st.session_state.user_id)
        if words:
            word_to_delete = st.selectbox(
                "Выберите слово для удаления:",
                options=[f"{w['word_ru']} - {w['word_en']}" for w in words],
                key="delete_select"
            )

            if st.button("🗑️ Удалить", type="secondary"):
                word_ru = word_to_delete.split(" - ")[0]
                if db.delete_word(st.session_state.user_id, word_ru):
                    st.success(f"Слово '{word_ru}' удалено из вашего словаря")
                    st.rerun()
                else:
                    st.error("Ошибка при удалении")
        else:
            st.info("У вас нет слов для удаления")

    # Вкладка "Статистика"
    with menu[3]:
        st.header("Ваша статистика изучения")

        stats = db.get_statistics(st.session_state.user_id)
        words = db.get_user_words(st.session_state.user_id)

        if stats and stats['total_attempts'] and stats['total_attempts'] > 0:
            total_words = stats['total_words']
            correct = stats['total_correct'] or 0
            attempts = stats['total_attempts'] or 0
            accuracy = (correct / attempts * 100) if attempts > 0 else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📚 Всего слов", total_words)
            with col2:
                st.metric("✅ Правильных ответов", correct)
            with col3:
                st.metric("📊 Точность", f"{accuracy:.1f}%")

            st.markdown("---")
            st.subheader("Детальная статистика по словам")

            # Таблица со статистикой
            stats_data = []
            for word in words:
                attempts_word = word['total_attempts'] or 0
                correct_word = word['correct_answers'] or 0
                word_accuracy = (correct_word / attempts_word * 100) if attempts_word > 0 else 0
                stats_data.append({
                    "Русское слово": word['word_ru'],
                    "Английский перевод": word['word_en'],
                    "Попыток": attempts_word,
                    "Правильно": correct_word,
                    "Точность": f"{word_accuracy:.1f}%"
                })

            df = pd.DataFrame(stats_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Пока нет статистики. Начните изучать слова в разделе 'Изучение'")

else:
    # Сообщение для неавторизованных пользователей
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h1>🇬🇧 Добро пожаловать в EnglishCard! 🇺🇸</h1>
        <h3>Изучайте английский язык с удовольствием!</h3>
        <p>👈 Войдите в систему, указав ваше имя в боковой панели</p>
    </div>
    """, unsafe_allow_html=True)

# Схема базы данных в подвале
if st.session_state.user_id:
    with st.expander("🗄️ Схема базы данных"):
        st.markdown("""
        ### Структура базы данных

        **Таблица users**
        - id (PRIMARY KEY) - идентификатор пользователя
        - username - имя пользователя
        - created_at - дата регистрации

        **Таблица base_words**
        - id (PRIMARY KEY) - идентификатор слова
        - word_ru - слово на русском
        - word_en - перевод на английский
        - category - категория слова

        **Таблица user_words**
        - id (PRIMARY KEY) - идентификатор записи
        - user_id (FOREIGN KEY) - связь с пользователем
        - word_ru - слово на русском
        - word_en - перевод на английский
        - correct_answers - количество правильных ответов
        - total_attempts - всего попыток
        - added_at - дата добавления

        ```
        users ──┐
                ├── user_words
        base_words
        ```
        """)