from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import NotAuthenticated, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins, viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.serializers import CustomAuthTokenEmailSerializer, FollowSerializer, CustomUserSerializer
from api.serializers import TagSerializer, IngridientSerializer, RecipeReadSerializer
from rest_framework.decorators import action

from food.models import Tag, Ingridient, Recipe
from users.models import User, Follow
from djoser.views import UserViewSet

FIRST_ELEM = 0


class MyAuthToken(ObtainAuthToken):
    """Получение токена пользователем."""
    serializer_class = CustomAuthTokenEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"auth_token": token.key})


class LogoutToken(APIView):
    """Удаление токена пользователя."""
    def post(self, request):
        if not request.user.is_anonymous:
            request.user.auth_token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise NotAuthenticated


class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
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


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = request.user
        queryset = User.objects.filter(pk=id)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(pages,
                                      data=request.data,
                                      many=True,
                                      context={'request':  request})
        if serializer.is_valid(raise_exception=True):
            Follow.objects.get_or_create(user=user, author=queryset[0])
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors)

    @action(detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscriber__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(pages,
                                      many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)
