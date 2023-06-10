import csv

from django.core.management.base import BaseCommand
from food.models import Ingredient

from foodgram.settings import BASE_DIR


def upload_ingridients():
    """Загружает ингридиенты в БД."""
    with open(
              BASE_DIR.parent.parent / 'data/ingredients.csv',
              encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')

        for row in csv_reader:
            Ingredient.objects.get_or_create(
                name=row['name'],
                measurement_unit=row[' measurement_unit']
            )


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        upload_ingridients()
