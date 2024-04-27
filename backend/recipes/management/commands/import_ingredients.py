import csv

from django.core.management.base import BaseCommand
from tqdm import tqdm

from recipes.models import Ingredient


def import_ingredients_from_csv(csv_file):
    """
    Function to import data from a CSV file
    into the database for the Ingredient model.

    Arguments:
      csv_file (str): Path to the CSV file.
    Usage:
      python manage.py import_ingredients data/ingredients.csv
    """
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        total_rows = sum(1 for row in reader)
        file.seek(0)
        with tqdm(total=total_rows,
                  desc='Importing ingredients',
                  unit=' row') as pbar:
            for row in reader:
                name, measurement_unit = row[0], row[1]
                ingredient, created = Ingredient.objects.get_or_create(
                    name=name, measurement_unit=measurement_unit
                )
                if created:
                    pbar.set_postfix({'New ingredient': name})
                else:
                    pbar.set_postfix({'Existing ingredient': name})
                pbar.update(1)


class Command(BaseCommand):
    help = 'Import ingredients from a CSV file'
    default_filename = 'data/ingredients.csv'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path',
                            nargs='?',
                            type=str,
                            default=self.default_filename,
                            help=(f'Path to the CSV file '
                                  f'(default: {self.default_filename})'))

    def handle(self, *args, **kwargs):
        import_ingredients_from_csv(kwargs['csv_file_path'])
        self.stdout.write(self.style.SUCCESS(
            'Ingredients import completed successfully.'))
