## Программное обеспечение для автоматизации построения, анализа и визуализации тактовых циклограмм работы роботизированных ячеек, используемых в производственных процессах

Система планирования проектов с визуализацией циклограмм для роботизированных производственных ячеек.

## Возможности

- Создание и управление проектами
- Добавление операций с настройкой времени выполнения
- Управление исполнителями
- Визуализация циклограмм с масштабированием
- Настройка зависимостей между операциями
- Экспорт в Excel
- Drag & Drop для изменения порядка операций
- Автоматический пересчёт времени с учётом зависимостей

## Требования

- **Python** 3.8+
- **Node.js** 18+
- **npm** (устанавливается с Node.js)
- **Docker** (опционально)

## Быстрый старт

### Вариант 1: Локальный запуск (без Docker)

#### Windows:

**Запуск:**
```cmd
cd Cicklogramus
start.bat
```

**Остановка:**
```cmd
stop.bat
```

#### Linux/macOS:

**Запуск:**
```bash
cd Cicklogramus
chmod +x start.sh stop.sh
./start.sh
```

**Остановка:**
```bash
./stop.sh
```

### Вариант 2: Запуск с Docker

```bash
cd Cicklogramus
docker-compose up --build
```

**Остановка:**
```bash
docker-compose down
```

## Что происходит автоматически при запуске

1. Проверка Python и Node.js
2. Создание виртуального окружения
3. Установка зависимостей
4. Создание SQLite базы данных
5. Применение миграций
6. Запуск backend на порту 8080
7. Запуск frontend на порту 3000

## Доступные адреса

| Сервис | URL |
|--------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8080/api |
| API документация | http://localhost:8080/swagger/ |
| Admin Panel | http://localhost:8080/admin |


## Полезные команды

### Backend

```bash
# Создать суперюзера для админки
cd backend
source ../venv/bin/activate  # Linux/macOS
..\venv\Scripts\activate     # Windows
python manage.py createsuperuser

# Применить миграции
python manage.py migrate

# Запустить сервер разработки
python manage.py runserver
```

### Frontend

```bash
cd Cicklogram-frontend

# Установить зависимости
npm install

# Запустить сервер разработки
npm run serve

# Собрать для продакшена
npm run build
```

## База данных

### Локальная разработка
Используется **SQLite** - создаётся автоматически при первом запуске.
Файл: `Cicklogramus/backend/db.sqlite3`

**Сброс базы данных:**
```bash
rm backend/db.sqlite3          # Linux/macOS
del backend\db.sqlite3         # Windows
./start.sh restart             # Пересоздать базу
```

### Docker (Production)
Используется **PostgreSQL** в контейнере.

## Технологии

### Backend
- Django 4.2
- Django REST Framework
- PostgreSQL / SQLite
- CORS headers

### Frontend
- Vue.js 3
- Axios
- Bootstrap 5
- SweetAlert2
