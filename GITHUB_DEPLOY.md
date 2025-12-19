# Инструкция по загрузке проекта на GitHub

## Что нужно от вас:

1. **URL вашего репозитория на GitHub**
   - Если репозитория еще нет, создайте его на GitHub:
     - Зайдите на https://github.com
     - Нажмите "New repository" (зеленая кнопка)
     - Назовите репозиторий (например: `edpro-platform`)
     - НЕ добавляйте README, .gitignore или лицензию (они уже есть в проекте)
     - Скопируйте URL репозитория (например: `https://github.com/ваш-username/edpro-platform.git`)

2. **Настройка Git (если еще не настроено)**
   - Выполните команды:
     ```bash
     git config --global user.name "Ваше Имя"
     git config --global user.email "your.email@example.com"
     ```

## Автоматическая загрузка (Windows):

1. Откройте файл `deploy_to_github.bat` в редакторе
2. Замените `YOUR_GITHUB_REPO_URL` на URL вашего репозитория
3. Запустите файл двойным кликом
4. Следуйте инструкциям на экране

## Автоматическая загрузка (macOS/Linux):

1. Сделайте скрипт исполняемым:
   ```bash
   chmod +x deploy_to_github.sh
   ```
2. Откройте файл `deploy_to_github.sh` в редакторе
3. Замените `YOUR_GITHUB_REPO_URL` на URL вашего репозитория
4. Запустите скрипт:
   ```bash
   ./deploy_to_github.sh
   ```

## Ручная загрузка (пошагово):

### Шаг 1: Инициализация git (если еще не сделано)

```bash
git init
```

### Шаг 2: Настройка git (если еще не настроено)

```bash
git config --global user.name "Ваше Имя"
git config --global user.email "your.email@example.com"
```

### Шаг 3: Добавление всех файлов

```bash
git add .
```

### Шаг 4: Создание первого коммита

```bash
git commit -m "Initial commit: EdPro Platform with full documentation"
```

### Шаг 5: Добавление remote репозитория

Замените `YOUR_GITHUB_REPO_URL` на URL вашего репозитория:

```bash
git remote add origin https://github.com/ваш-username/edpro-platform.git
```

Если remote уже существует, обновите URL:

```bash
git remote set-url origin https://github.com/ваш-username/edpro-platform.git
```

### Шаг 6: Переименование ветки в main (если нужно)

```bash
git branch -M main
```

### Шаг 7: Загрузка на GitHub

```bash
git push -u origin main
```

Если GitHub попросит авторизацию:
- Используйте Personal Access Token (PAT) вместо пароля
- Создайте токен: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
- Или используйте GitHub CLI: `gh auth login`

## Проверка

После загрузки откройте ваш репозиторий на GitHub и убедитесь, что все файлы загружены:
- ✅ README.md
- ✅ requirements.txt
- ✅ Папка studyhub/
- ✅ Папка docs/ с диаграммами и скриншотами

## Если возникли проблемы:

### Ошибка: "remote origin already exists"
```bash
git remote remove origin
git remote add origin YOUR_GITHUB_REPO_URL
```

### Ошибка: "Authentication failed"
- Используйте Personal Access Token вместо пароля
- Или настройте SSH ключи

### Ошибка: "Permission denied"
- Убедитесь, что у вас есть права на запись в репозиторий
- Проверьте правильность URL репозитория

