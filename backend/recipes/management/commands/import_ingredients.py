"""python manage.py import_ingredients 'data/ingredients.csv'"""

import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def import_ingredients_from_csv(csv_file):
    """
    Функция для импорта данных из CSV файла
    в базу данных для модели Ingredient.

    Аргументы:
    csv_file (str): Путь к CSV файлу.
    """
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            name = row[0]
            measurement_unit = row[1]
            if not Ingredient.objects.filter(
                    name=name, measurement_unit=measurement_unit).exists():
                Ingredient.objects.create(
                    name=name, measurement_unit=measurement_unit)
                print(f'Ингредиент "{name}" успешно добавлен.')
            else:
                print(f'Ингредиент "{name}" уже существует в базе данных.')


class Command(BaseCommand):
    help = 'Import ingredients from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str,
                            help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file_path']
        import_ingredients_from_csv(csv_file_path)
