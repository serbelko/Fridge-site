Этот проект представляет собой веб-приложение для управления продуктами в холодильнике, списком покупок и аналитикой потребления. Пользователи могут регистрироваться, входить в систему, добавлять продукты в холодильник, сканировать QR-коды для автоматического добавления продуктов, а также управлять списком покупок. Приложение также предоставляет возможность отслеживать сроки годности продуктов и анализировать их использование.
Основные функции:
Регистрация и аутентификация пользователей.
Управление продуктами в холодильнике.
Сканирование QR-кодов для добавления продуктов.
Управление списком покупок.
Аналитика потребления продуктов.

## 🛠️ Инструкция по установке и развертыванию
Для работы проекта необходимо установить Python 3.8 или выше. Затем установите все необходимые зависимости, выполнив следующие команды:

# Клонируйте репозиторий
`git clone https://github.com/serbelko/Fridge-site.git`
# Установите зависимости
`pip install -r requirements.txt`
# Применение миграций
Проект использует SQLAlchemy для работы с базой данных. Для инициализации базы данных выполните следующие шаги:
Убедитесь, что у вас установлена база данных (например, SQLite, PostgreSQL или MySQL).
Настройте подключение к базе данных в файле config.py (если требуется).
Выполните миграции для создания таблиц в базе данных:
`flask db upgrade`
# Запуск приложения
После установки зависимостей и настройки базы данных, вы можете запустить приложение:
`python run.py`

Приложение будет доступно по адресу: http://localhost:5000.

# 🗂️ Структура проекта
Проект состоит из следующих основных файлов и папок:
__init__.py: Инициализация приложения Flask, настройка базы данных, миграций и системы аутентификации.
models.py: Определение моделей базы данных (например, User, Product, Fridge, ShoppingList, Analytics).
forms.py: Формы для регистрации и входа пользователя.
routes.py: Основные маршруты приложения (главная страница, продукты, аналитика, список покупок).
fridge.py: Логика работы с холодильником (добавление, удаление продуктов, перемещение из списка покупок).
scan.py: Логика сканирования QR-кодов и обработки данных.
signIN_and_UP.py: Логика регистрации и входа пользователя.
run.py: Запуск приложения и инициализация базы данных.
migrations/: Папка с миграциями базы данных, созданными с помощью Alembic.
templates/: HTML-шаблоны для отображения страниц.
static/: Статические файлы (CSS, JavaScript, изображения).

🛠️ Используемые технологии
Flask: Микрофреймворк для создания веб-приложений на Python.
SQLAlchemy: ORM для работы с базой данных.
Flask-Login: Управление аутентификацией пользователей.
Flask-WTF: Работа с формами.
Alembic: Управление миграциями базы данных.
OpenCV: Обработка изображений и сканирование QR-кодов.
Bootstrap: Фронтенд-фреймворк для создания интерфейса.
