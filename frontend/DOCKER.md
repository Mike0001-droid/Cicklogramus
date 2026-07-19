# Frontend Docker - Cicklogramus

## Структура

- `Dockerfile` - сборка Vue.js приложения с nginx
- `nginx.conf` - конфиг nginx для production (проксирует на Railway backend)
- `nginx.local.conf` - конфиг nginx для local dev (проксирует на локальный backend)
- `.dockerignore` - исключения для Docker контекста
- `Railway.toml` - конфиг для деплоя на Railway

## Локальный запуск (с backend)

```bash
cd C:\Users\major\cicklo3\backend\Cicklogramus
docker-compose -f docker-compose-local.yml up --build
```

Frontend будет доступен на http://localhost:3000
Backend API будет проксироваться через nginx на http://backend:8080

## Локальный запуск (только frontend)

```bash
cd C:\Users\major\cicklo3\frontend\Cicklogram-frontend
docker build --build-arg NGINX_CONF=nginx.local.conf -t cicklogram-frontend .
docker run -p 3000:80 cicklogram-frontend
```

## Деплой на Railway

1. **Создайте новый проект в Railway**
2. **Добавьте GitHub репозиторий**
3. **Railway автоматически определит Dockerfile и соберёт проект**

Frontend будет проксировать API запросы на:
```
https://cicklogramus-production.up.railway.app/api/
```

## Переменные окружения (необязательно)

Если нужно изменить backend URL, отредактируйте `nginx.conf`:
```nginx
proxy_pass https://your-backend-url/api/;
```

## Архитектура

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Browser   │──────│  Nginx       │──────│  Railway    │
│  (localhost)│      │  (Frontend)  │      │  Backend    │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ├── /api/*  → proxy to backend
                            └── /*      → Vue app
```

## Nginx конфигурация

**Production (nginx.conf):**
- Проксирует `/api/*` на Railway backend
- Обслуживает статику из `/dist`
- SPA fallback (все маршруты → index.html)

**Local (nginx.local.conf):**
- Проксирует `/api/*` на локальный backend (http://backend:8080)
- То же самое для статики и SPA
