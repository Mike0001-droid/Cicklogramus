@echo off
REM Скрипт для остановки Cicklogramus в Windows

echo Остановка Cicklogramus...

REM Останавливаем все процессы Python
taskkill /f /im python.exe /fi "WINDOWTITLE eq Cicklogramus*" 2>nul

REM Останавливаем все процессы Node.js
taskkill /f /im node.exe /fi "WINDOWTITLE eq Cicklogramus*" 2>nul

echo [OK] Все серверы остановлены
pause
