from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import User


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""
    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password',)
        read_only_fields = ('id',)


class CustomAuthTokenEmailSerializer(serializers.Serializer):
    """
    Сериализатор для получения токена,
    используя электронный адрес для авторизации пользователя.
    """
    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password",),
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            if not user:
                msg = _('Authentication credentials were not provided.')
                raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
