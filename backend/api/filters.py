from django_filters import rest_framework as filters
from users.models import User

from .models import Ingredient, Recipe, Tag


class RecipeFilter(filters.FilterSet):
    """Фильтрсет для рецептов."""
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(recipe_favorite__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(recipe_shop_cart__user=self.request.user)
        return queryset


class IngredientFilter(filters.FilterSet):
    """Фильтерсет для ингредиентов."""
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
