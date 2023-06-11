# Generated by Django 4.2.1 on 2023-06-10 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0011_rename_ingridient_ingredient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingridientforrecipe',
            name='amount',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveIntegerField(verbose_name='Время приготовления'),
        ),
    ]
