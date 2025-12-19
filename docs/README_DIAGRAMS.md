# Инструкции по созданию диаграмм

## ER-диаграмма базы данных

### Вариант 1: dbdiagram.io

1. Перейдите на https://dbdiagram.io
2. Скопируйте код ниже в редактор
3. Нажмите "Export" → "Export as PNG"
4. Сохраните файл как `docs/er_diagram.png`

### Код для dbdiagram.io:

```sql
Table User {
  id int [pk, increment]
  username varchar
  email varchar
  password varchar
  first_name varchar
  last_name varchar
  is_staff boolean
  is_superuser boolean
  date_joined datetime
}

Table UserProfile {
  id int [pk, increment]
  user_id int [ref: > User.id, unique]
  role varchar [note: 'student, tutor, admin']
  bio text
  phone varchar
  birth_date date
  avatar varchar
  created_at datetime
  updated_at datetime
}

Table Category {
  id int [pk, increment]
  name varchar
  description text
}

Table Course {
  id int [pk, increment]
  title varchar
  description text
  full_description text
  price decimal
  is_free boolean
  level varchar [note: 'beginner, middle, advanced']
  is_popular boolean
  author_id int [ref: > User.id]
  category_id int [ref: > Category.id]
  duration_hours int
  is_published boolean
  created_at datetime
  updated_at datetime
}

Table Module {
  id int [pk, increment]
  course_id int [ref: > Course.id]
  title varchar
  description text
  order int
  created_at datetime
  updated_at datetime
}

Table Lesson {
  id int [pk, increment]
  module_id int [ref: > Module.id]
  title varchar
  content text
  order int
  duration_minutes int
  is_published boolean
  created_at datetime
  updated_at datetime
}

Table Enrollment {
  id int [pk, increment]
  user_id int [ref: > User.id]
  course_id int [ref: > Course.id]
  enrolled_at datetime
  completed boolean
}

Table Progress {
  id int [pk, increment]
  user_id int [ref: > User.id]
  lesson_id int [ref: > Lesson.id]
  completed boolean
  completed_at datetime
  created_at datetime
  updated_at datetime
}

Table Review {
  id int [pk, increment]
  course_id int [ref: > Course.id]
  user_id int [ref: > User.id]
  rating int [note: '1-5']
  text text
  created_at datetime
  updated_at datetime
}

Table Order {
  id int [pk, increment]
  user_id int [ref: > User.id]
  created_at datetime
  status varchar [note: 'new, paid, delivering']
}

Table OrderItem {
  id int [pk, increment]
  order_id int [ref: > Order.id]
  course_id int [ref: > Course.id]
  price decimal
}

Table AssistantCategory {
  id int [pk, increment]
  name varchar
}

Table AssistantQuestion {
  id int [pk, increment]
  category_id int [ref: > AssistantCategory.id]
  question varchar
  answer text
}

Table SupportRequest {
  id int [pk, increment]
  name varchar
  contact varchar
  message text
  contact_type varchar
  status varchar [note: 'pending, completed']
  created_at datetime
  completed_at datetime
}
```

### Вариант 2: draw.io

1. Перейдите на https://app.diagrams.net/
2. Создайте новую диаграмму
3. Используйте элементы "Entity" для таблиц
4. Соедините таблицы линиями, показывающими связи
5. Экспортируйте как PNG: File → Export as → PNG
6. Сохраните как `docs/er_diagram.png`

## Архитектурная схема

### Использование draw.io

1. Перейдите на https://app.diagrams.net/
2. Создайте новую диаграмму
3. Добавьте следующие блоки:

#### Блоки для схемы:

1. **Браузер (Client)**
   - Прямоугольник с текстом "Браузер (Client)"
   - Подпись: "HTML, CSS, JavaScript"

2. **Django Backend**
   - Прямоугольник с текстом "Django Backend"
   - Внутри подблоки:
     - URL Router
     - Views
     - Models
     - Templates
     - Forms
     - Mixins

3. **База данных**
   - Цилиндр с текстом "SQLite Database"
   - Подпись: "Хранение данных"

4. **File Storage**
   - Прямоугольник с текстом "Media Files"
   - Подпись: "Аватары, изображения"

5. **Session Storage**
   - Прямоугольник с текстом "Session Storage"
   - Подпись: "Корзина, сессии"

#### Стрелки (поток данных):

- Браузер → Django Backend (HTTP запросы)
- Django Backend → База данных (SQL запросы)
- Django Backend → File Storage (чтение/запись файлов)
- Django Backend → Session Storage (чтение/запись сессий)
- Django Backend → Браузер (HTML ответы)

4. Экспортируйте как PNG: File → Export as → PNG
5. Сохраните как `docs/architecture.png`

### Альтернативный вариант (текстовое описание):

```
┌─────────────┐
│   Браузер   │
│  (Client)   │
└──────┬──────┘
       │ HTTP запросы
       ▼
┌─────────────────────────────────┐
│      Django Backend             │
│  ┌──────────┐  ┌──────────┐   │
│  │URL Router│  │  Views   │   │
│  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐   │
│  │ Models   │  │Templates │   │
│  └──────────┘  └──────────┘   │
└──────┬──────────────────────────┘
       │
       ├───► SQLite Database
       │
       ├───► Media Files
       │
       └───► Session Storage
```

## Скриншоты

Добавьте скриншоты главных страниц приложения в папку `docs/screenshots/`:

1. `home.png` - Главная страница
2. `courses.png` - Каталог курсов
3. `course_detail.png` - Детальная страница курса
4. `my_courses.png` - Личный кабинет
5. `cart.png` - Корзина

### Как сделать скриншоты:

1. Запустите сервер разработки: `python manage.py runserver`
2. Откройте нужные страницы в браузере
3. Сделайте скриншоты (Windows: Win+Shift+S, Mac: Cmd+Shift+4)
4. Сохраните в папку `docs/screenshots/` с соответствующими именами

