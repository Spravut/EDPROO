# Generated manually
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0011_alter_userprofile_role'),
    ]

    operations = [
        # Удаляем старое поле processed
        migrations.RemoveField(
            model_name='supportrequest',
            name='processed',
        ),
        # Добавляем новое поле status
        migrations.AddField(
            model_name='supportrequest',
            name='status',
            field=models.CharField(
                choices=[('pending', 'В рассмотрении'), ('completed', 'Выполнено')],
                default='pending',
                max_length=20,
                verbose_name='Статус',
                help_text='Статус обработки обращения'
            ),
        ),
        # Добавляем поле contact_type
        migrations.AddField(
            model_name='supportrequest',
            name='contact_type',
            field=models.CharField(
                blank=True,
                help_text='Тип обращения (вопрос, техническая проблема и т.д.)',
                max_length=50,
                null=True,
                verbose_name='Тип обращения'
            ),
        ),
        # Добавляем поле completed_at
        migrations.AddField(
            model_name='supportrequest',
            name='completed_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Дата, когда обращение было выполнено',
                null=True,
                verbose_name='Дата выполнения'
            ),
        ),
    ]

