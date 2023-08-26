import base64
import webcolors

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from recipes.models import (Favorite, Ingredient, IngredientsInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import User

MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 600
MIN_AMOUNT_INGREDIENTS = 1


class Hex2NameColor(serializers.Field):
    """Вспомогательный класс для работы с цветом."""
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    """Вспомогательный класс для работы с изображениями."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(UserSerializer):
    """Сеарилизатор для пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username', 'id', 'email', 'first_name',
            'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if (request and request.user.is_authenticated):
            return obj.following.exists()
        return False


class CreateUserSerializer(UserCreateSerializer):
    """Сериализатор для создания нового пользователя."""
    username = serializers.RegexField(regex=r'^[\w.@+-]+\Z',
                                      max_length=150,
                                      validators=[UniqueValidator(
                                          queryset=User.objects.all())])
    email = serializers.EmailField(max_length=254,
                                   validators=[UniqueValidator(
                                       queryset=User.objects.all())])

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'password'
        )

    def validate(self, data):
        username = User.objects.filter(
            username=data.get('username')).first()
        email = User.objects.filter(
            email=data.get('email')).first()
        if username is None and email is not None:
            raise serializers.ValidationError(
                'Пользователь с такой почтой уже зарегистрирован'
            )
        if username is not None and email is None:
            raise serializers.ValidationError(
                'Пользователь с таким именем уже зарегистрирован'
            )
        if username is not None and email is not None:
            raise serializers.ValidationError(
                'Пользователь с таким именем и почтой уже зарегистрирован'
            )
        return data


class RecipeMiniFieldSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения краткой информации о рецепте."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """Сеарилизатор для подписок."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')
        read_only_fields = ('id', 'email', 'username',
                            'is_subscribed',
                            'first_name', 'last_name',
                            'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if (request and request.user.is_authenticated):
            return obj.following.exists()
        return False

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        queryset = obj.author_recipe.all()
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return RecipeMiniFieldSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.author_recipe.count()


class TagSerializer(serializers.ModelSerializer):
    """Сеарилизатор для тэгов."""
    name = serializers.CharField(
        max_length=200,
        validators=[UniqueValidator(
            queryset=Tag.objects.all())],
    )
    color = Hex2NameColor()
    slug = serializers.CharField(
        max_length=200,
        validators=[UniqueValidator(
            queryset=Tag.objects.all())],
    )

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сеарилизатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сеарилизатор для ингредиентов в рецептах."""
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount', 'name',
                  'measurement_unit')


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    """Сеарилизатор для добавления ингредиента в рецепт."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount')

    def validate_amount(self, amount):
        if amount < MIN_AMOUNT_INGREDIENTS:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше или равно 1!'
            )
        return amount


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сеарилизатор для показа рецепта."""
    tags = TagSerializer(many=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='recipe_ingredients'
    )
    author = UserSerializer()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if (request is not None and request.user.is_authenticated):
            return obj.recipe_favorite.exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if (request is not None and request.user.is_authenticated):
            return obj.recipe_shop_cart.exists()
        return False

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'author',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сеарилизатор для создания рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = AddIngredientToRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'name', 'tags',
            'ingredients', 'image', 'text',
            'cooking_time'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'text', 'cooking_time'),
                message='Такой рецепт уже есть!'
            )
        ]

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data

    def validate(self, data):
        ingredients = data['ingredients']
        ing_list = []
        for ingredient in ingredients:
            if ingredient['id'] in ing_list:
                raise serializers.ValidationError(
                    'Ингридиенты не должны повторяться!'
                )
            ing_list.append(ingredient['id'])
        return data

    def validate_cooking_time(self, cooking_time):
        if cooking_time < MIN_COOKING_TIME:
            raise serializers.ValidationError(
                'Время готовки должно быть больше 1 минуты!')
        if cooking_time > MAX_COOKING_TIME:
            raise serializers.ValidationError(
                'Время готовки не должно быть больше 10 часов!')
        return cooking_time

    def ingredients_and_tags_for_recipe(self, recipe, ingredients, tags):
        recipe.tags.set(tags)
        for ingredient in ingredients:
            amount = ingredient['amount']
            current_ingredient = Ingredient.objects.get(id=ingredient['id'])
            IngredientsInRecipe.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=amount
            )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.ingredients_and_tags_for_recipe(recipe, ingredients, tags)
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        self.ingredients_and_tags_for_recipe(instance, ingredients, tags)
        instance.save()
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""
    user = UserSerializer()
    recipe = RecipeReadSerializer(many=True)

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Данный рецепт уже есть в избранном!'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeMiniFieldSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины."""
    user = UserSerializer()
    recipe = RecipeReadSerializer(many=True)

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Данный рецепт уже есть в корзине!'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeMiniFieldSerializer(
            instance.recipe,
            context={'request': request}
        ).data
