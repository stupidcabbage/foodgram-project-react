# Generated by Django 4.2.1 on 2023-06-10 22:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0013_rename_ingridientforrecipe_ingredientforrecipe_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='tag',
            new_name='tags',
        ),
    ]
