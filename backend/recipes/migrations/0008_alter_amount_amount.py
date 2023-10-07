# Generated by Django 3.2.12 on 2022-03-09 11:15

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20220309_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amount',
            name='amount',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0.01)], verbose_name='Количество'),
        ),
    ]