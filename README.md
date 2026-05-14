# О проекте

Проект TeamFinder — это веб-приложение, сервис поиска участников для IT-проектов, разработанный на Django, с использованием PostgreSQL для хранения данных.

**Оглавление**

- [О проекте](#о-проекте)
- [Запуск TeamFinder](#запуск-teamfinder)
    - [Docker Compose (автоматизированная сборка)](#docker-compose-автоматизированная-сборка)
    - [Локальная разработка (ручная сборка)](#локальная-разработка-ручная-сборка)
- [Переменные окружения](#переменные-окружения)

# Запуск TeamFinder

### Docker Compose (автоматизированная сборка)

1. Клонировать репозиторий
2. Скопировать `.env_example` -> `.env` и заполнить его (секретный ключ, БД). Подробнее см. в секции [переменные окружения](#переменные-окружения).
3. Выполнить:
```sh
docker compose up -d
```

    Docker-сборка автоматически выполняет миграции, собирает статику и заполняет базу тестовыми данными.

4. Открыть: http://localhost:8000


### Локальная разработка (ручная сборка)

1. Клонировать репозиторий

git clone [https://github.com/archsaurus/team-finder](https://github.com/archsaurus/team-finder.git)

2. Создать виртуальное окружение:

```sh
python3 -m venv venv

source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate # Windows

pip install --upgrade pip
pip install -r requirements.txt
```

3. Скопировать и заполнить файл [переменных окружения](#переменные-окружения) .env.

4. Настроить PostgreSQL (локально или Docker).

5. Последовательно выполнить команды:

```sh
python manage.py makemigrations
python manage.py migrate

python manage.py collectstatic --noinput

python manage.py create_test_data  # Загружаем тестовые данные в базу

python manage.py runserver
```

6. Открыть: http://127.0.0.1:8000

# Переменные окружения

| Переменная            | Назначение                                                                                                                                                 |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **DJANGO_SECRET_KEY** | Секретный ключ Django, используемый для подписи cookie и токенов. Можно сгенерировать при помощи `get_random_secret_key` из `django.core.management.utils` |
| **DJANGO_DEBUG**      | Режим отладки. Установите `True` во время разработки.                                                                                                      |
| **POSTGRES_DB**       | Имя базы данных PostgreSQL, которую будет использовать Django.                                                                                             |
| **POSTGRES_USER**     | Имя пользователя PostgreSQL.                                                                                                                               |
| **POSTGRES_PASSWORD** | Пароль пользователя PostgreSQL.                                                                                                                            |
| **POSTGRES_HOST**     | Адрес сервера БД. В случае локальной разработки localhost.                                                                                                 |
| **POSTGRES_PORT**     | Порт подключения к БД (по умолчанию `5432`).                                                                                                               |
| **TASK_VERSION**      | Номер варианта задания. Используется для определения набора HTML-шаблонов. В данной реализации выбран вариант 1.                                                                         |

---
