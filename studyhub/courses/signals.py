from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматически создаем профиль при создании пользователя (только если профиль еще не создан)"""
    if created:
        # Создаем профиль только если его еще нет (форма регистрации может создать его раньше)
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'role': 'student'}  # Дефолтная роль, если не указана
        )