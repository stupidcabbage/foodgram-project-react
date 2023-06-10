from api.serializers import (CustomAuthTokenEmailSerializer,
                             CustomUserSerializer, FollowSerializer)
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Follow, User


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
