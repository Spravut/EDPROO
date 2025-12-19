@echo off
REM Скрипт для загрузки проекта на GitHub
REM Замените YOUR_GITHUB_REPO_URL на URL вашего репозитория

echo ========================================
echo Загрузка проекта на GitHub
echo ========================================
echo.

REM Проверка, инициализирован ли git
if not exist .git (
    echo Инициализация git репозитория...
    git init
    echo.
)

REM Настройка git (если еще не настроено)
echo Проверка настроек git...
git config user.name >nul 2>&1
if errorlevel 1 (
    echo ВНИМАНИЕ: Git не настроен!
    echo Выполните команды:
    echo   git config --global user.name "Ваше Имя"
    echo   git config --global user.email "your.email@example.com"
    echo.
    pause
    exit /b 1
)

REM Добавление всех файлов
echo Добавление файлов в git...
git add .

REM Проверка статуса
echo.
echo Статус репозитория:
git status

echo.
echo ========================================
echo Следующие шаги:
echo ========================================
echo.
echo 1. Создайте коммит:
echo    git commit -m "Initial commit: EdPro Platform"
echo.
echo 2. Добавьте remote (замените YOUR_GITHUB_REPO_URL):
echo    git remote add origin YOUR_GITHUB_REPO_URL
echo    ИЛИ если remote уже существует:
echo    git remote set-url origin YOUR_GITHUB_REPO_URL
echo.
echo 3. Загрузите на GitHub:
echo    git branch -M main
echo    git push -u origin main
echo.
echo ========================================
pause

