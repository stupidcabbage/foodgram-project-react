from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, response, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateUpdateSerializer,
                             RecipeReadSerializer, ShoppingCartSerializer,
                             TagSerializer)
from food.models import Favorite, Recipe, ShoppingCart
from services import ingredient as ingr
from services import model as m
from services import recipe, tag

SERIALIZERS_MODEL = {
    Favorite: FavoriteSerializer,
    ShoppingCart: ShoppingCartSerializer
}


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Вьюсет для отображения тэгов."""
    queryset = tag.get_all_tags()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngridientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """Вьюсет отображения ингридиентов."""
    queryset = ingr.get_all_ingredients()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет отображения рецептов."""
    queryset = recipe.get_all_recipes()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateUpdateSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == "POST":
            return self._create_to(ShoppingCart, recipe, request)
        return self._delete_from(ShoppingCart, recipe, request)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == "POST":
            return self._create_to(Favorite, recipe, request)
        return self._delete_from(Favorite, recipe, request)

    @action(detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):

        ingredients = ingr.get_sum_amount(user=request.user)

        shopping_list = (
            'Список покупок: \n\n'
        )
        for ingredient in ingredients:
            shopping_list += (
                f'- {ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]})'
                f' - {ingredient["total_amount"]}'
            ) + '\n'

        name = 'shop_list.txt'
        response = HttpResponse(shopping_list,
                                content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={name}'

        return response

    def _create_to(self, model, recipe, request):
        """Создает модель, предварительно прогнав через сериализатор."""
        if m.is_exists(request.user, recipe, model):
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self._validate_data(model, request, recipe)
        m.create(request.user, recipe, model)
        return response.Response(serializer.data,
                                 status=status.HTTP_201_CREATED)

    def _delete_from(self, model, recipe, request):
        """Удаляет модель, предварительно прогнав через сериализатор."""
        if not m.is_exists(request.user, recipe, model):
            return Response({'errors': 'Рецепт уже удален!'},
                            status=status.HTTP_400_BAD_REQUEST)

        self._validate_data(model, request, recipe)
        m.delete(request.user, recipe, model)
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def _validate_data(self, model, request, recipe):
        serializer = SERIALIZERS_MODEL[model](
            recipe,
            data=request.data,
            context={"request": request})
        serializer.is_valid(raise_exception=True)
        return serializer
