# Generated by Django 3.2.15 on 2023-11-14 23:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_subscription_users_subscription_prevent_self_follow'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('username',), 'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
    ]