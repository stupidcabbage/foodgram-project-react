# Generated by Django 4.2.1 on 2023-06-07 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0003_alter_tag_colour_alter_tag_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Название'),
        ),
    ]