from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из csv файлов в БД'

    def handle(self, **options):
        with open("ingredients.csv") as ingredients:
            ingredients_list = []
            for ingredient in ingredients:
                ingred = ingredient.split(',')
                ingredients_list.append(Ingredient(
                    name=ingred[0],
                    measurement_unit=ingred[1]
                ))
            Ingredient.objects.bulk_create(ingredients_list)

        self.stdout.write(self.style.SUCCESS('Данные успешно загружены'))
