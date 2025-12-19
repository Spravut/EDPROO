from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import Category, Course, UserProfile


class Command(BaseCommand):
    help = 'Создает примерные категории и курсы для тестирования системы подбора'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Удалить существующие категории и курсы перед созданием новых',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Удаление существующих данных...'))
            Course.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Данные удалены.'))

        # Создаем или получаем преподавателя
        tutor, created = User.objects.get_or_create(
            username='tutor_demo',
            defaults={
                'email': 'tutor@example.com',
                'first_name': 'Демо',
                'last_name': 'Преподаватель'
            }
        )
        if created:
            tutor.set_password('demo12345')
            tutor.save()
            UserProfile.objects.get_or_create(
                user=tutor,
                defaults={'role': 'tutor'}
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Создан преподаватель: {tutor.username}'))

        # Создаем категории
        categories_data = [
            {
                'name': 'Программирование',
                'description': 'Курсы по программированию на различных языках'
            },
            {
                'name': 'Веб-разработка',
                'description': 'Создание веб-сайтов и веб-приложений'
            },
            {
                'name': 'Мобильная разработка',
                'description': 'Разработка мобильных приложений для iOS и Android'
            },
            {
                'name': 'Дизайн',
                'description': 'Веб-дизайн, UI/UX, графика и иллюстрация'
            },
            {
                'name': 'Базы данных',
                'description': 'Работа с базами данных, SQL и NoSQL'
            },
            {
                'name': 'Машинное обучение',
                'description': 'Искусственный интеллект, нейронные сети и data science'
            },
            {
                'name': 'DevOps',
                'description': 'Развертывание, автоматизация и мониторинг'
            },
            {
                'name': 'Кибербезопасность',
                'description': 'Безопасность информационных систем'
            },
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Создана категория: {category.name}'))

        # Создаем курсы
        courses_data = [
            # Программирование
            {
                'title': 'Python для начинающих',
                'description': 'Изучите основы программирования на Python. От переменных до функций и классов.',
                'full_description': 'Полный курс по Python для новичков. Вы изучите синтаксис, типы данных, функции, классы и многое другое.',
                'category': categories['Программирование'],
                'level': 'beginner',
                'price': 0,
                'duration_hours': 40,
                'is_popular': True,
            },
            {
                'title': 'Продвинутый Python',
                'description': 'Углубленное изучение Python: декораторы, генераторы, метаклассы и оптимизация.',
                'full_description': 'Для тех, кто уже знает основы Python и хочет углубить свои знания.',
                'category': categories['Программирование'],
                'level': 'advanced',
                'price': 5000,
                'duration_hours': 60,
            },
            {
                'title': 'Java с нуля',
                'description': 'Освойте Java - один из самых популярных языков программирования в мире.',
                'full_description': 'Курс по Java для начинающих программистов.',
                'category': categories['Программирование'],
                'level': 'beginner',
                'price': 3000,
                'duration_hours': 50,
            },
            {
                'title': 'JavaScript для начинающих',
                'description': 'Изучите JavaScript - язык программирования для веб-разработки.',
                'full_description': 'Основы JavaScript: переменные, функции, объекты, DOM и многое другое.',
                'category': categories['Программирование'],
                'level': 'beginner',
                'price': 0,
                'duration_hours': 30,
                'is_popular': True,
            },
            
            # Веб-разработка
            {
                'title': 'HTML и CSS с нуля',
                'description': 'Создавайте красивые веб-страницы с помощью HTML и CSS.',
                'full_description': 'Основы веб-разработки: структура HTML, стили CSS, адаптивная верстка.',
                'category': categories['Веб-разработка'],
                'level': 'beginner',
                'price': 0,
                'duration_hours': 25,
            },
            {
                'title': 'Django для веб-разработки',
                'description': 'Создавайте полноценные веб-приложения на Django - мощном фреймворке Python.',
                'full_description': 'Изучите Django от основ до создания полноценных веб-приложений с базой данных.',
                'category': categories['Веб-разработка'],
                'level': 'middle',
                'price': 6000,
                'duration_hours': 70,
                'is_popular': True,
            },
            {
                'title': 'React - современный фронтенд',
                'description': 'Освойте React - самую популярную библиотеку для создания пользовательских интерфейсов.',
                'full_description': 'React, компоненты, хуки, роутинг и работа с API.',
                'category': categories['Веб-разработка'],
                'level': 'middle',
                'price': 5500,
                'duration_hours': 65,
            },
            {
                'title': 'Full Stack разработка',
                'description': 'Станьте full stack разработчиком: изучите и фронтенд, и бэкенд.',
                'full_description': 'Комплексный курс по full stack разработке: React, Node.js, базы данных.',
                'category': categories['Веб-разработка'],
                'level': 'advanced',
                'price': 12000,
                'duration_hours': 120,
            },
            
            # Мобильная разработка
            {
                'title': 'Разработка Android приложений',
                'description': 'Создавайте мобильные приложения для Android на Java и Kotlin.',
                'full_description': 'Разработка Android приложений с нуля: UI, работа с данными, публикация в Google Play.',
                'category': categories['Мобильная разработка'],
                'level': 'middle',
                'price': 7000,
                'duration_hours': 80,
            },
            {
                'title': 'iOS разработка на Swift',
                'description': 'Создавайте приложения для iPhone и iPad на языке Swift.',
                'full_description': 'Разработка iOS приложений: Swift, UIKit, SwiftUI, Core Data.',
                'category': categories['Мобильная разработка'],
                'level': 'middle',
                'price': 8000,
                'duration_hours': 85,
            },
            {
                'title': 'React Native - кроссплатформенная разработка',
                'description': 'Создавайте мобильные приложения для iOS и Android одновременно.',
                'full_description': 'React Native позволяет писать один код для обеих платформ.',
                'category': categories['Мобильная разработка'],
                'level': 'middle',
                'price': 6500,
                'duration_hours': 75,
            },
            
            # Дизайн
            {
                'title': 'Веб-дизайн для начинающих',
                'description': 'Изучите основы веб-дизайна: композиция, цвет, типографика.',
                'full_description': 'Основы веб-дизайна и создание макетов в Figma.',
                'category': categories['Дизайн'],
                'level': 'beginner',
                'price': 2000,
                'duration_hours': 30,
            },
            {
                'title': 'UI/UX дизайн',
                'description': 'Создавайте удобные и красивые интерфейсы. Изучите принципы UX дизайна.',
                'full_description': 'Проектирование пользовательских интерфейсов и улучшение пользовательского опыта.',
                'category': categories['Дизайн'],
                'level': 'middle',
                'price': 4500,
                'duration_hours': 50,
            },
            {
                'title': 'Графический дизайн в Photoshop',
                'description': 'Освойте Adobe Photoshop для создания графики и обработки изображений.',
                'full_description': 'Работа с Photoshop: слои, маски, фильтры, ретушь фотографий.',
                'category': categories['Дизайн'],
                'level': 'beginner',
                'price': 3000,
                'duration_hours': 35,
            },
            
            # Базы данных
            {
                'title': 'SQL для начинающих',
                'description': 'Изучите основы работы с базами данных и язык SQL.',
                'full_description': 'SQL запросы, создание таблиц, связи между таблицами, индексы.',
                'category': categories['Базы данных'],
                'level': 'beginner',
                'price': 0,
                'duration_hours': 20,
            },
            {
                'title': 'PostgreSQL - продвинутый уровень',
                'description': 'Углубленное изучение PostgreSQL: оптимизация, репликация, партиционирование.',
                'full_description': 'Продвинутые возможности PostgreSQL для опытных разработчиков.',
                'category': categories['Базы данных'],
                'level': 'advanced',
                'price': 5000,
                'duration_hours': 55,
            },
            {
                'title': 'MongoDB и NoSQL',
                'description': 'Изучите работу с NoSQL базами данных на примере MongoDB.',
                'full_description': 'MongoDB: документы, коллекции, агрегации, индексы.',
                'category': categories['Базы данных'],
                'level': 'middle',
                'price': 4000,
                'duration_hours': 40,
            },
            
            # Машинное обучение
            {
                'title': 'Введение в машинное обучение',
                'description': 'Основы машинного обучения и data science на Python.',
                'full_description': 'Изучите основы ML: линейная регрессия, классификация, кластеризация.',
                'category': categories['Машинное обучение'],
                'level': 'beginner',
                'price': 6000,
                'duration_hours': 60,
            },
            {
                'title': 'Глубокое обучение с TensorFlow',
                'description': 'Создавайте нейронные сети с помощью TensorFlow и Keras.',
                'full_description': 'Нейронные сети, сверточные сети, рекуррентные сети, трансформеры.',
                'category': categories['Машинное обучение'],
                'level': 'advanced',
                'price': 10000,
                'duration_hours': 90,
            },
            {
                'title': 'Data Science на Python',
                'description': 'Анализ данных, визуализация и предсказательное моделирование.',
                'full_description': 'Pandas, NumPy, Matplotlib, Scikit-learn для анализа данных.',
                'category': categories['Машинное обучение'],
                'level': 'middle',
                'price': 7000,
                'duration_hours': 70,
            },
            
            # DevOps
            {
                'title': 'Docker и контейнеризация',
                'description': 'Изучите Docker для контейнеризации приложений.',
                'full_description': 'Docker, Docker Compose, создание образов, оркестрация контейнеров.',
                'category': categories['DevOps'],
                'level': 'middle',
                'price': 4500,
                'duration_hours': 45,
            },
            {
                'title': 'Kubernetes для разработчиков',
                'description': 'Оркестрация контейнеров с помощью Kubernetes.',
                'full_description': 'Kubernetes: поды, сервисы, деплойменты, масштабирование.',
                'category': categories['DevOps'],
                'level': 'advanced',
                'price': 8000,
                'duration_hours': 80,
            },
            
            # Кибербезопасность
            {
                'title': 'Основы кибербезопасности',
                'description': 'Изучите основы защиты информационных систем.',
                'full_description': 'Угрозы, уязвимости, методы защиты, криптография.',
                'category': categories['Кибербезопасность'],
                'level': 'beginner',
                'price': 3500,
                'duration_hours': 40,
            },
        ]

        created_count = 0
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults={
                    'author': tutor,
                    'description': course_data['description'],
                    'full_description': course_data.get('full_description', course_data['description']),
                    'category': course_data['category'],
                    'level': course_data['level'],
                    'price': course_data['price'],
                    'duration_hours': course_data['duration_hours'],
                    'is_published': True,
                    'is_popular': course_data.get('is_popular', False),
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Создан курс: {course.title}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Готово! Создано курсов: {created_count}\n'
                f'  Категорий: {len(categories)}\n'
                f'  Преподаватель: {tutor.username} (пароль: demo12345)'
            )
        )

