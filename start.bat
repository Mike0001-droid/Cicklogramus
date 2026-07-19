@echo off
REM Устанавливаем кодировку UTF-8 для поддержки русского языка
chcp 65001 >nul
REM Скрипт для запуска Cicklogramus в Windows
REM Автор: Claude Code

setlocal enabledelayedexpansion

echo ========================================
echo   Запуск Cicklogramus
echo ========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не установлен. Установите Python 3.8+
    pause
    exit /b 1
)

REM Проверка Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js не установлен. Установите Node.js 18+
    pause
    exit /b 1
)

echo [INFO] Настройка backend...
cd /d "%~dp0"

REM Создаём виртуальное окружение если его нет
if not exist "venv" (
    echo [INFO] Создание виртуального окружения Python...
    python -m venv venv
)

REM Активируем виртуальное окружение
call venv\Scripts\activate.bat

REM Устанавливаем зависимости
echo [INFO] Установка зависимостей Python...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Создаём .env если его нет
if not exist ".env" (
    echo [INFO] Создание .env файла...
    (
        echo # Django Settings
        echo DEBUG=True
        echo SECRET_KEY=django-insecure-local-development
        echo ALLOWED_HOSTS=localhost,127.0.0.1
        echo.
        echo # Database (SQLite)
        echo DB_ENGINE=django.db.backends.sqlite3
        echo DB_NAME=db.sqlite3
        echo.
        echo # Backend Port
        echo BACKEND_PORT=8080
        echo.
        echo # CORS Settings
        echo CORS_ALLOW_CREDENTIALS=True
        echo CORS_ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080,http://localhost:3000
    ) > .env
)

REM Применяем миграции
echo [INFO] Применение миграций...
cd backend
python manage.py migrate --no-input
cd ..

REM Создаём директорию для логов
if not exist "logs" mkdir logs

echo.
echo [INFO] Запуск Django backend на порту 8080...
cd backend
start "Cicklogramus Backend" cmd /k "python manage.py runserver 0.0.0.0:8080"
cd ..

REM Ждём запуска backend
timeout /t 3 /nobreak >nul

echo [INFO] Запуск Vue.js frontend на порту 3000...
cd ..\Cicklogram-frontend

REM Устанавливаем зависимости если нужно
if not exist "node_modules" (
    echo [INFO] Установка зависимостей Node.js...
    npm install --silent
)

REM Устанавливаем переменную окружения для API
set VUE_APP_API_URL=http://localhost:8080/api

start "Cicklogramus Frontend" cmd /k "npm run serve"
cd ..\Cicklogramus

REM Ждём запуска frontend
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   Система успешно запущена!
echo ========================================
echo.
echo Frontend:     http://localhost:3000
echo Backend API:  http://localhost:8080/api
echo Admin panel:  http://localhost:8080/admin
echo.
echo Для остановки закройте окна с серверами
echo или запустите stop.bat
echo.
pause
