from api.models import Ingredient
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Импорт данных из csv файлов в БД'

    def handle(self, **options):
        with open("ingredients.csv") as ingredients:
            for ingredient in ingredients:
                ingred = ingredient.split(',')
                Ingredient.objects.get_or_create(
                    name=ingred[0],
                    measurement_unit=ingred[1]
                )

        self.stdout.write(self.style.SUCCESS('Данные успешно загружены'))
