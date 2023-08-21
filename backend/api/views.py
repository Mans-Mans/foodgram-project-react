from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .models import (Favorite, Follow, Ingredient, IngredientsInRecipe, Recipe,
                     ShoppingCart, Tag)
from .permissions import IsAuthorOrReadOnly
from .serializers import (FollowSerializer, IngredientSerializer,
                          IngredientsInRecipe, RecipeCreateSerializer,
                          RecipeMiniFieldSerializer, RecipeReadSerializer,
                          TagSerializer, UserSerializer)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = PageNumberPagination
    serializer_class = UserSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def follow(self, request, id):
        following = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if Follow.objects.filter(user=request.user,
                                     following=following).exists():
                return Response({'errors': 'Подписка уже оформлена!'},
                                status=status.HTTP_400_BAD_REQUEST)
            if request.user == following:
                return Response({'errors': 'Нельзя подписаться на себя!'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowSerializer(
                following,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=request.user,
                                  following=following)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(
                Follow, user=request.user, following=following
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'],
            url_path='subscriptions',
            permission_classes=(AllowAny,))
    def follows(self, request):
        queryset = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для IngredientSerializer."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    search_fields = ('^name', )
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для TagSerializer."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для RecipeSerializer."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    serializer_class = RecipeReadSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['list', 'retrive']:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def get_queryset(self):
        recipe = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()
        return recipe

    @action(detail=True, methods=('POST', 'DELETE'),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(user=request.user,
                                       recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже в избранном!'},
                                status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=request.user,
                                    recipe=recipe)
            serializer = RecipeMiniFieldSerializer(recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(
                Favorite, user=request.user,
                recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'],
            url_path='shopping_cart',
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже в корзине!'},
                                status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=request.user,
                                        recipe=recipe)
            serializer = RecipeMiniFieldSerializer(recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'],
            url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated, ])
    def download_cart(self, request):
        """Отправка файла со списком покупок."""
        ingredients = IngredientsInRecipe.objects.filter(
            recipe__recipe_shop_cart__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            amount=Sum('amount'))
        download_cart_list = ('Mans-foodgram.\n'
                              'Ингредиенты:\n')
        for ingredient in ingredients:
            download_cart_list += (
                f"{ingredient['ingredient__name']}  - "
                f"{ingredient['amount']}"
                f"{ingredient['ingredient__measurement_unit']}\n"
            )
        response = HttpResponse(download_cart_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response
