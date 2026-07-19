# Docker Django REST Framework

## Запуск проекта через Docker

### Требования
- Docker Desktop установлен и запущен

### Быстрый старт

1. **Скопируйте файл переменных окружения:**
   ```bash
   cp .env.example .env
   ```

2. **Запустите контейнеры:**
   ```bash
   docker-compose up --build
   ```

   Или в фоновом режиме:
   ```bash
   docker-compose up -d --build
   ```

3. **API будет доступен по адресу:**
   - Backend API: http://localhost:8000/api/
   - Swagger документация: http://localhost:8000/swagger/
   - Admin панель: http://localhost:8000/admin/

### Полезные команды

**Посмотреть логи:**
```bash
docker-compose logs -f
```

**Остановить контейнеры:**
```bash
docker-compose down
```

**Перезапустить бэкенд:**
```bash
docker-compose restart backend
```

**Выполнить миграции вручную:**
```bash
docker-compose exec backend python manage.py migrate
```

**Создать суперпользователя:**
```bash
docker-compose exec backend python manage.py createsuperuser
```

**Войти в оболочку Django:**
```bash
docker-compose exec backend python manage.py shell
```

### Структура

- `Dockerfile` - образ для Django приложения
- `docker-compose.yml` - оркестрация сервисов (backend + PostgreSQL)
- `.dockerignore` - исключения для Docker контекста
- `.env.example` - шаблон переменных окружения

### Переменные окружения

Основные переменные в `.env`:
- `DEBUG` - режим отладки (True/False)
- `SECRET_KEY` - секретный ключ Django
- `ALLOWED_HOSTS` - разрешённые хосты
- `DB_NAME` - имя базы данных
- `DB_USER` - пользователь PostgreSQL
- `DB_PASSWORD` - пароль PostgreSQL
- `DB_HOST` - хост базы данных (в docker: `db`)
- `DB_PORT` - порт PostgreSQL

### Troubleshooting

**База данных не подключается:**
```bash
docker-compose down -v
docker-compose up --build
```

**Ошибка миграций:**
```bash
docker-compose exec backend python manage.py migrate --run-syncdb
```
