# Generated by Django 4.2.1 on 2023-06-10 20:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0010_alter_ingridient_name'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Ingridient',
            new_name='ingredient',
        ),
    ]
