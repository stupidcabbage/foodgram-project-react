from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from api.serializers import FollowRecipeSerializer

from food.models import Recipe
from .models import User, Follow


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""
    class Meta:
        model = User
        fields = ("email",
                  "id",
                  "username",
                  "first_name",
                  "last_name",
                  "password",)
        read_only_fields = ("id",)


class CustomAuthTokenEmailSerializer(serializers.Serializer):
    """
    Сериализатор для получения токена,
    используя электронный адрес для авторизации пользователя.
    """
    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password",),
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(request=self.context.get("request"),
                                email=email, password=password)

            if not user:
                msg = _("Authentication credentials were not provided.")
                raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def validate(self, attrs):
        user = self.context.get('request').user
        if user.id == attrs.id:
            raise serializers.ValidationError(
                _('Subscribing to yourself is prohibited.'))

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        recipe = Recipe.objects.filter(
            author=obj)
        serializer = FollowRecipeSerializer(data=recipe, many=True)
        print(serializer.error_messages)
        if not serializer.is_valid():
            return serializer.data

    def get_recipes_count(self, obj):
        recipes_count = Recipe.objects.filter(
            author=obj).count()
        return recipes_count
