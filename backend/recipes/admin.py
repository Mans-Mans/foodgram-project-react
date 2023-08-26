from django.contrib import admin

from .models import (Favorite, Follow, Ingredient, IngredientsInRecipe, Recipe,
                     ShoppingCart, Tag)


class IngredientAdmin(admin.ModelAdmin):
    """Админка ингредиентов."""
    list_display = ('pk', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    list_filter = ('name', )
    search_fields = ('name', )


class IngredientsInRecipeInline(admin.TabularInline):
    """Админка отображения ингредиентов при создании рецепта."""
    model = IngredientsInRecipe


class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""
    list_display = ('pk', 'name', 'author',
                    'in_favorites_amount')
    list_editable = ('name', 'author')
    readonly_fields = ('in_favorites_amount',)
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', )
    empty_value_display = '-пусто-'
    inlines = [
        IngredientsInRecipeInline,
    ]

    def tags(self, row):
        return ','.join([x.name for x in row.tags.all()])

    def ingredients(self, row):
        return ','.join([x.name for x in row.ingredients.all()])

    def in_favorites_amount(self, obj):
        return obj.recipe_favorite.count()
    in_favorites_amount.short_description = 'Кол-во добавлений в избранное'

class TagAdmin(admin.ModelAdmin):
    """Админка тэгов."""
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'


class IngredientsInRecipeAdmin(admin.ModelAdmin):
    """Админка ингредиентов в рецептах."""
    list_display = ('pk', 'ingredient', 'recipe', 'amount')
    list_editable = ('ingredient', 'recipe', 'amount')
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка корзины."""
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    """Админка избранного."""
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    """Админка подписок."""
    list_display = ('pk', 'user', 'following')
    list_editable = ('user', 'following')
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(IngredientsInRecipe, IngredientsInRecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Follow, FollowAdmin)
