from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateUpdateSerializer,
                             RecipeReadSerializer, ShoppingCartSerializer,
                             ShortRecipeSerializer, TagSerializer)
from django.shortcuts import get_object_or_404
from food.models import Favourites, Ingredient, Recipe, ShoppingCart, Tag
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


class IngridientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """Вьюсет отображения ингридиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет отображения рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)

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
