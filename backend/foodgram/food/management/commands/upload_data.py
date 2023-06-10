import csv
from django.core.management.base import BaseCommand
from food.models import Ingridient
import os

path = r'F:/Dev_Ya/diplom/foodgram-project-react/data/ingredients.csv'
assert os.path.isfile(path)


def upload_ingridients():
    """Загружает ингридиенты в БД."""
    with open(path, encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')

        for row in csv_reader:
            Ingridient.objects.get_or_create(
                name=row['name'],
                measurement_unit=row[' measurement_unit']
            )


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        upload_ingridients()
