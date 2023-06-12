from datetime import datetime

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateUpdateSerializer,
                             RecipeReadSerializer, ShoppingCartSerializer,
                             TagSerializer)
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from food.models import (Favourites, Ingredient, IngredientForRecipe, Recipe,
                         ShoppingCart, Tag)
from rest_framework import filters, mixins, response, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated

SERIALIZERS_MODEL = {
    Favourites: FavoriteSerializer,
    ShoppingCart: ShoppingCartSerializer
}


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Вьюсет для отображения тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngridientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """Вьюсет отображения ингридиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет отображения рецептов."""
    queryset = Recipe.objects.all()
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
        if request.method == "DELETE":
            return self._delete_from(ShoppingCart, recipe, request)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == "POST":
            return self._create_to(Favourites, recipe, request)
        if request.method == "DELETE":
            return self._delete_from(Favourites, recipe, request)

    @action(detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user

        ingredients = IngredientForRecipe.objects.filter(
            recipe__shoppingcart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        today = datetime.today()
        shopping_list = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {today:%d.%m.%y}\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        shopping_list += f'\n\nFoodgram ({today:%Y})'

        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response

    def _create_to(self, model, recipe, request):
        """Создает модель, предварительно прогнав через сериализатор."""
        serializer = self._validate_data(model, request, recipe)
        model.objects.create(user=request.user, recipe=recipe)
        return response.Response(serializer.data,
                                 status=status.HTTP_201_CREATED)

    def _delete_from(self, model, recipe, request):
        """Удаляет модель, предварительно прогнав через сериализатор."""
        self._validate_data(model, request, recipe)
        model.objects.filter(user=request.user, recipe=recipe).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def _validate_data(self, model, request, recipe):
        serializer = SERIALIZERS_MODEL[model](
            recipe,
            data=request.data,
            context={"request": request})
        serializer.is_valid(raise_exception=True)
        return serializer
