#!/bin/bash

# Скрипт для остановки Cicklogramus

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[OK] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Переходим в директорию проекта
cd "$(dirname "$0")"

print_info "Остановка серверов..."

# Останавливаем backend
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null || true
        print_success "Backend остановлен (PID: $BACKEND_PID)"
    fi
    rm -f logs/backend.pid
fi

# Останавливаем frontend
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_success "Frontend остановлен (PID: $FRONTEND_PID)"
    fi
    rm -f logs/frontend.pid
fi

# Убиваем все остальные процессы
pkill -f "manage.py runserver" 2>/dev/null || true
pkill -f "vue-cli-service serve" 2>/dev/null || true

print_success "Все серверы остановлены"
