from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.serializers import CustomAuthTokenEmailSerializer, UserSerializer


class MyAuthToken(ObtainAuthToken):
    """Получение токена пользователем."""
    serializer_class = CustomAuthTokenEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'auth_token': token.key})


class LogoutToken(APIView):
    """Удаление токена пользователя."""
    def post(self, request):
        if not request.user.is_anonymous:
            request.user.auth_token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED,
                        data={'detail': NotAuthenticated.default_detail})
