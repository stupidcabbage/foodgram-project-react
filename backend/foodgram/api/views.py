from api.serializers import (FavouriteSerializer, IngridientSerializer,
                             RecipeReadSerializer, TagSerializer)
from django.shortcuts import get_object_or_404
from food.models import Favourites, ingredient, Recipe, Tag
from rest_framework import filters, mixins, response, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Вьюсет для отображения тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngridientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """Вьюсет отображения ингридиентов."""
    queryset = ingredient.objects.all()
    serializer_class = IngridientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class RecipeViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """Вьюсет отображения рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (AllowAny,)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favourite(self, request, pk):
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
