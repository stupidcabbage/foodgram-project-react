from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import NotAuthenticated, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins, viewsets, filters
from rest_framework.permissions import AllowAny
from users.serializers import CustomAuthTokenEmailSerializer
from api.serializers import TagSerializer, IngridientSerializer, RecipeSerializer

from food.models import Tag, Ingridient, Recipe

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


class RecipeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)