# Cicklogramus Frontend

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

---

## Docker

### Структура Docker файлов

- `Dockerfile` - сборка Vue.js + nginx
- `nginx.conf` - для Railway (прокси на Railway backend)
- `nginx.local.conf` - для docker-compose с backend (прокси на backend контейнер)
- `nginx.standalone.conf` - для standalone (прокси на backend на хост-машине)
- `docker-compose.yml` - standalone запуск frontend
- `Railway.toml` - конфиг для деплоя на Railway

### Способы запуска

#### 1. Local Development (Backend на хост-машине)

**Шаг 1: Запустите backend**
```bash
cd C:\Users\major\cicklo3\backend\Cicklogramus
docker-compose up
# Backend будет доступен на localhost:8080
```

**Шаг 2: Запустите frontend**
```bash
cd C:\Users\major\cicklo3\frontend\Cicklogram-frontend
docker-compose up --build
# Frontend будет доступен на localhost:3000
```

#### 2. Local Development (Backend + Frontend вместе)

Используйте docker-compose из backend репозитория:
```bash
cd C:\Users\major\cicklo3\backend\Cicklogramus
docker-compose -f docker-compose-local.yml up --build
```

#### 3. Development без Docker

```bash
npm install
npm run serve
# Frontend на localhost:8080
```

#### 4. Production на Railway

Просто добавьте репозиторий в Railway - он автоматически задеплоится через Dockerfile.

Frontend будет проксировать API на: `https://cicklogramus-production.up.railway.app/api/`

### Полезные команды

**Пересобрать контейнер:**
```bash
docker-compose up --build --force-recreate
```

**Посмотреть логи:**
```bash
docker-compose logs -f
```

**Остановить:**
```bash
docker-compose down
```

## Nginx конфиги

| Конфиг | Для чего | Proxy pass |
|--------|----------|------------|
| `nginx.conf` | Railway | `https://cicklogramus-production.up.railway.app/api/` |
| `nginx.local.conf` | Docker compose с backend | `http://backend:8080/api/` |
| `nginx.standalone.conf` | Standalone frontend | `http://host.docker.internal:8080/api/` |

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
