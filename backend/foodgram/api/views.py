from api.serializers import (FavouriteSerializer, IngredientSerializer,
                             RecipeCreateUpdateSerializer,
                             RecipeReadSerializer, TagSerializer)
from django.shortcuts import get_object_or_404
from food.models import Favourites, Ingredient, Recipe, Tag
from rest_framework import filters, mixins, response, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated


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
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateUpdateSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == "POST":
            serializer = FavouriteSerializer(
                recipe,
                data=request.data,
                context={"request": request})
            serializer.is_valid(raise_exception=True)
            Favourites.objects.create(user=user, recipe=recipe)
            return response.Response(serializer.data,
                                     status=status.HTTP_200_OK)

        if request.method == "DELETE":
            serializer = FavouriteSerializer(
                recipe,
                data=request.data,
                context={"request": request})
            serializer.is_valid(raise_exception=True)
            Favourites.objects.filter(user=user, recipe=recipe).delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
