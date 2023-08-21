from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    """Модель тэгов."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тэга',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        default="#FF0000",
        verbose_name='Цвет тэга',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг',
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название продукта',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецептов."""
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги рецепта',
    )
    author = models.ForeignKey(
        User,
        related_name='author_recipe',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsInRecipe',
        verbose_name='Ингредиенты',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='foodgram/image/',
        verbose_name='Фото рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления в минутах',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientsInRecipe(models.Model):
    """Модель ингредиентов в рецепте."""
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredients_in_recipe',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return f'{self.recipe} - {self.ingredient} - {self.amount}'


class ShoppingCart(models.Model):
    """Модель корзины."""
    user = models.ForeignKey(
        User,
        related_name='buyer',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_shop_cart',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_shopcart'
            )
        ]


class Favorite(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(
        User,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_favorite',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ['recipe']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_favorite'
            )
        ]


class Follow(models.Model):
    """Модель подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='user_and_following_different'
            ),
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_follower',
            ),
        ]
