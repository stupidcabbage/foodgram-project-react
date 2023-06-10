from api.serializers import (IngridientSerializer, RecipeReadSerializer,
                             TagSerializer)
from food.models import Ingridient, Recipe, Tag
from rest_framework import filters, mixins, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

FIRST_ELEM = 0


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    "Вьюсет для отображения тэгов."
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        queryset = Tag.objects.filter(pk=self.kwargs["pk"])
        serializer = TagSerializer(queryset, many=True)
        if serializer.data:
            return Response(serializer.data[FIRST_ELEM])
        raise NotFound


class IngridientViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def retrieve(self, request, *args, **kwargs):
        queryset = Ingridient.objects.filter(pk=self.kwargs["pk"])
        serializer = IngridientSerializer(queryset, many=True)
        if serializer.data:
            return Response(serializer.data[FIRST_ELEM])
        raise NotFound


class RecipeViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (AllowAny,)
