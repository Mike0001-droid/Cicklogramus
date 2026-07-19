# Быстрый запуск Cicklogramus

## Локальный запуск (без Docker)

### Windows

**Запуск:**
```cmd
start.bat
```

**Остановка:**
```cmd
stop.bat
```

### Linux/macOS

**Запуск:**
```bash
chmod +x start.sh
./start.sh
```

**Остановка:**
```bash
./stop.sh
```

## Что происходит автоматически:

1. Проверка Python и Node.js
2. Создание виртуального окружения
3. Установка всех зависимостей
4. Создание SQLite базы данных
5. Применение миграций
6. Запуск backend на порту 8080
7. Запуск frontend на порту 3000

## Доступные адреса:

| Сервис | URL |
|--------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8080/api |
| Admin Panel | http://localhost:8080/admin |

## Требования:

- **Python** 3.8+
- **Node.js** 18+
- **npm** (устанавливается с Node.js)

## Полезные команды:

```bash
# Перезапуск
./start.sh restart   # Linux/macOS
start.bat            # Windows (запустите снова)

# Просмотр логов
tail -f logs/backend.log   # Linux/macOS
type logs\backend.log      # Windows

# Создать суперюзера для админки
cd backend
source ../venv/bin/activate  # Linux/macOS
..\venv\Scripts\activate     # Windows
python manage.py createsuperuser
```

## Запуск с Docker:

```bash
cd Cicklogramus
docker-compose up --build
```

## Возможные проблемы:

### Порт занят
**Windows:**
```cmd
netstat -ano | findstr :8080
taskkill /PID <номер_процесса> /F
```

**Linux/macOS:**
```bash
lsof -ti:8080 | xargs kill -9
```

### Ошибка зависимостей
```bash
# Python
pip install --upgrade pip
pip install -r requirements.txt

# Node.js
npm install
```

## Структура проекта:

```
Cickloproject/
├── Cicklogramus/          # Backend (Django)
│   ├── backend/           # Django проект
│   ├── start.sh           # Скрипт запуска (Linux/macOS)
│   ├── start.bat          # Скрипт запуска (Windows)
│   └── stop.bat           # Скрипт остановки (Windows)
│
└── Cicklogram-frontend/   # Frontend (Vue.js)
    ├── src/               # Исходный код
    └── package.json       # Зависимости
```

## База данных:

Используется **SQLite** - создаётся автоматически при первом запуске.
Файл: `Cicklogramus/backend/db.sqlite3`

Для сброса базы данных:
```bash
rm backend/db.sqlite3          # Linux/macOS
del backend\db.sqlite3         # Windows
./start.sh restart             # Пересоздать базу
```
