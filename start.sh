#!/bin/bash

# Скрипт для запуска Cicklogramus в режиме разработки с SQLite
# Автор: Claude Code
# Дата: 2025

set -e  # Остановить при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[OK] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

# Проверка зависимостей
check_dependencies() {
    print_info "Проверка зависимостей..."

    # Проверка Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 не установлен. Установите Python 3.8+"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python $PYTHON_VERSION найден"

    # Проверка Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js не установлен. Установите Node.js 18+"
        exit 1
    fi

    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION найден"

    # Проверка npm
    if ! command -v npm &> /dev/null; then
        print_error "npm не установлен"
        exit 1
    fi

    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION найден"
}

# Настройка backend
setup_backend() {
    print_info "Настройка backend..."

    # Переходим в директорию backend
    cd "$(dirname "$0")"

    # Создаём виртуальное окружение если его нет
    if [ ! -d "venv" ]; then
        print_info "Создание виртуального окружения Python..."
        python3 -m venv venv
        print_success "Виртуальное окружение создано"
    fi

    # Активируем виртуальное окружение
    print_info "Активация виртуального окружения..."
    source venv/bin/activate

    # Устанавливаем зависимости
    print_info "Установка зависимостей Python..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    print_success "Зависимости Python установлены"

    # Создаём .env если его нет
    if [ ! -f ".env" ]; then
        print_info "Создание .env файла..."
        cat > .env << EOF
# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-local-development-$(openssl rand -hex 32)
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite - создается автоматически)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Backend Port
BACKEND_PORT=8080

# CORS Settings
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080,http://localhost:3000
CORS_PREFLIGHT_MAX_AGE=3600

# CSRF Settings
CSRF_TRUSTED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
EOF
        print_success ".env файл создан"
    fi

    # Применяем миграции
    print_info "Применение миграций базы данных..."
    cd backend
    python manage.py migrate --no-input
    print_success "Миграции применены"

    cd ..
}

# Настройка frontend
setup_frontend() {
    print_info "Настройка frontend..."

    # Переходим в директорию frontend
    cd "../Cicklogram-frontend"

    # Устанавливаем зависимости если нужно
    if [ ! -d "node_modules" ]; then
        print_info "Установка зависимостей Node.js..."
        npm install --silent
        print_success "Зависимости Node.js установлены"
    fi

    cd "../Cicklogramus"
}

# Запуск серверов
start_servers() {
    print_info "Запуск серверов..."

    # Создаём директорию для логов
    mkdir -p logs

    # Запускаем backend в фоновом режиме
    print_info "Запуск Django backend на порту 8080..."
    cd backend
    source ../venv/bin/activate

    # Проверяем, занят ли порт
    if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        print_warning "Порт 8080 уже занят. Пытаемся остановить процесс..."
        pkill -f "manage.py runserver" || true
        sleep 2
    fi

    nohup python manage.py runserver 0.0.0.0:8080 > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../logs/backend.pid
    cd ..

    # Ждём запуска backend
    sleep 3

    # Проверяем, что backend запустился
    if curl -s http://localhost:8080/api > /dev/null 2>&1; then
        print_success "Backend запущен (PID: $BACKEND_PID)"
    else
        print_error "Backend не запустился. Проверьте логи: logs/backend.log"
        exit 1
    fi

    # Запускаем frontend
    print_info "Запуск Vue.js frontend на порту 8081..."
    cd ../Cicklogram-frontend

    # Проверяем, занят ли порт
    if lsof -Pi :8081 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        print_warning "Порт 8081 уже занят. Пытаемся остановить процесс..."
        pkill -f "vue-cli-service serve" || true
        sleep 2
    fi

    # Устанавливаем переменную окружения для API
    export VUE_APP_API_URL=http://localhost:8080/api

    nohup npm run serve > ../Cicklogramus/logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../Cicklogramus/logs/frontend.pid

    cd ../Cicklogramus

    # Ждём запуска frontend
    sleep 5

    # Выводим информацию о запуске
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    print_success "Система успешно запущена!"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Frontend:     http://localhost:3000"
    echo "Backend API:  http://localhost:8080/api"
    echo "Admin panel:  http://localhost:8080/admin"
    echo ""
    echo "Логи:"
    echo "   Backend:  tail -f logs/backend.log"
    echo "   Frontend: tail -f logs/frontend.log"
    echo ""
    echo "Остановка:"
    echo "   ./stop.sh или ./start.sh --stop"
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
}

# Остановка серверов
stop_servers() {
    print_info "Остановка серверов..."

    # Останавливаем backend
    if [ -f "logs/backend.pid" ]; then
        BACKEND_PID=$(cat logs/backend.pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill $BACKEND_PID
            print_success "Backend остановлен"
        fi
        rm logs/backend.pid
    fi

    # Останавливаем frontend
    if [ -f "logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill $FRONTEND_PID
            print_success "Frontend остановлен"
        fi
        rm logs/frontend.pid
    fi

    # Убиваем все остальные процессы
    pkill -f "manage.py runserver" || true
    pkill -f "vue-cli-service serve" || true

    print_success "Все серверы остановлены"
}

# Главная функция
main() {
    case "${1:-start}" in
        start)
            check_dependencies
            setup_backend
            setup_frontend
            start_servers
            ;;
        stop)
            stop_servers
            ;;
        restart)
            stop_servers
            sleep 2
            check_dependencies
            setup_backend
            setup_frontend
            start_servers
            ;;
        --help|-h)
            echo "Использование: $0 [start|stop|restart]"
            echo ""
            echo "Команды:"
            echo "  start    - Запустить все сервисы (по умолчанию)"
            echo "  stop     - Остановить все сервисы"
            echo "  restart  - Перезапустить все сервисы"
            echo "  --help   - Показать эту справку"
            ;;
        *)
            print_error "Неизвестная команда: $1"
            echo "Используйте --help для справки"
            exit 1
            ;;
    esac
}

# Запуск
main "$@"
