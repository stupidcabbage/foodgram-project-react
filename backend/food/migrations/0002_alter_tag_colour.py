# Generated by Django 4.2.1 on 2023-06-16 19:38

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='colour',
            field=colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=18, samples=[('#E26C2D', 'orange'), ('#49B64E', 'green'), ('#8775fD2', 'purple')], verbose_name='Цвет'),
        ),
    ]
