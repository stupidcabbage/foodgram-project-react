import base64

from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from djoser.serializers import UserCreateSerializer, UserSerializer
from food.models import Favourites, Ingredient, Recipe, Tag
from rest_framework import serializers
from users.models import Follow, User


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с тэгами."""
    class Meta:
        model = Tag
        fields = ("id", "name", "colour", "slug")


class IngridientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингридиентами."""
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class Base64ImageField(serializers.ImageField):
    """Перевод картинки из base64 в нормальный формат."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с рецептами в отображении подписок."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


class CustomUserSerializer(UserSerializer):
    """Кастомный сериализатор для работы с пользователями."""
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
        """Получение поля is_subscribed."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов (GET)."""
    tag = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingridients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "tag", "author",
                  "ingridients", "name", "image",
                  "text", "cooking_time")
        read_only_fields = ("id", "author")

    def get_ingridients(self, obj):
        """Получение поля ингридиенты."""
        recipe = obj
        ingridients = recipe.ingridients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingridientforrecipe__amount')
        )
        return ingridients


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
    """Сериализатор для работы с подписками."""
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
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, attrs):
        """Валидация полей подписок."""
        request = self.context.get('request')
        author = self._args[0]
        follow = Follow.objects.filter(
            user=request.user, author=author).exists()

        if request.method == 'POST':
            if request.user.id == author.id:
                raise serializers.ValidationError({
                    'error': 'Подписка на себя - запрещена.'})
            if follow:
                raise serializers.ValidationError({
                    'error': 'Вы уже подписаны на данного пользователя.'})

        if request.method == 'DELETE':
            if not follow:
                raise serializers.ValidationError({
                    "error": "Вы не подписаны."})
        return attrs

    def get_is_subscribed(self, obj):
        """Получение поля is_subscribed."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        """Получение поля рецепта."""
        recipe = Recipe.objects.filter(author=obj)
        serializer = ShortRecipeSerializer(recipe, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Получение поля recipes_count, отображающий кол-во рецептов,
        созданных пользователем."""
        recipes_count = Recipe.objects.filter(author=obj).count()
        return recipes_count


class FavouriteSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с избранным."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = fields

    def validate(self, attrs):
        """Валидация полей для добавления в избранные."""
        request = self.context.get('request')
        recipe: Recipe = self._args[0]
        favourite = Favourites.objects.filter(
            user=request.user, recipe=recipe).exists()

        if request.method == 'POST':
            if favourite:
                raise serializers.ValidationError({
                    'error': 'Рецепт уже в избранном.'})
        if request.method == 'DELETE':
            if not favourite:
                raise serializers.ValidationError({
                    'error': 'У вас нет ничего в избранном.'})
        return attrs
