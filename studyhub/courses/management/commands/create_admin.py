from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import UserProfile


class Command(BaseCommand):
    help = 'Создает администратора платформы'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Имя пользователя администратора')
        parser.add_argument('email', type=str, help='Email администратора')
        parser.add_argument('--password', type=str, help='Пароль администратора (если не указан, будет запрошен)')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options.get('password')

        # Проверяем, существует ли пользователь
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'Пользователь с именем "{username}" уже существует!'))
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'Пользователь с email "{email}" уже существует!'))
            return

        # Запрашиваем пароль, если не указан
        if not password:
            from getpass import getpass
            password = getpass('Введите пароль: ')
            password_confirm = getpass('Подтвердите пароль: ')
            if password != password_confirm:
                self.stdout.write(self.style.ERROR('Пароли не совпадают!'))
                return
            if len(password) < 8:
                self.stdout.write(self.style.ERROR('Пароль должен содержать минимум 8 символов!'))
                return

        # Создаем пользователя
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.is_staff = True  # Доступ к админке Django
            user.is_superuser = True  # Суперпользователь Django
            user.save()

            # Создаем профиль с ролью администратора
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': 'admin'}
            )
            
            if not created:
                # Если профиль уже существует, обновляем роль
                profile.role = 'admin'
                profile.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Администратор "{username}" успешно создан!\n'
                    f'  Email: {email}\n'
                    f'  Роль: Администратор\n'
                    f'  Доступ к Django админке: Да'
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при создании администратора: {e}'))

