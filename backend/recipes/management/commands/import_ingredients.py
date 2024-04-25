import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def import_ingredients_from_csv(csv_file):
    """
    Function to import data from a CSV file
    into the database for the Ingredient model.

    Arguments:
      csv_file (str): Path to the CSV file.
    Usage:
      python manage.py import_ingredients 'data/ingredients.csv
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
                print(f'Ingredient "{name}" successfully added.')
            else:
                print(f'Ingredient "{name}" already exists in the database.')


class Command(BaseCommand):
    help = 'Import ingredients from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str,
                            help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file_path']
        import_ingredients_from_csv(csv_file_path)
