# Generated by Django 4.2.1 on 2023-06-13 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0017_rename_favourites_favorites'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default=None, null=True, upload_to='media/recipes/images'),
        ),
    ]