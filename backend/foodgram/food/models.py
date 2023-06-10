import re

from django.core.validators import RegexValidator
from django.db import models
from users.models import User


class Ingredient(models.Model):
    """Ингридиент."""
    name = models.CharField(
        'Название',
        max_length=200)
    measurement_unit = models.CharField('Мера измерения', max_length=200)

    class Meta:
        verbose_name = 'Игридиент'
        verbose_name_plural = 'Игридиенты'

    def __str__(self):
        return f"{self.name} в {self.measurement_unit}"


class Tag(models.Model):
    """Тэг."""
    COLOURS = [
        ('#E26C2D', 'orange'),
        ('#49B64E', 'green'),
        ('#8775fD2', 'purple')
    ]

    name = models.CharField('Название',
                            max_length=200,
                            unique=True)
    colour = models.CharField('Цвет',
                              max_length=200,
                              unique=True,
                              choices=COLOURS)
    slug = models.SlugField(
        'Тэг',
        unique=True,
        max_length=200,
        validators=[
            RegexValidator(regex=re.compile(r"^[-a-zA-Z0-9_]+$"),
                           message='Проверьте правильность написания никнейма')
            ])

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт."""
    author = models.ForeignKey(
        verbose_name='Автор публикации',
        to=User,
        on_delete=models.CASCADE,
        related_name='author')
    name = models.CharField(
        'Название',
        max_length=200)
    text = models.TextField(
        'Описание')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления')
    ingredients = models.ManyToManyField(
        verbose_name='Ингридиенты',
        to=Ingredient,
        through="IngredientForRecipe")
    tags = models.ManyToManyField(
        verbose_name='Тэги',
        to=Tag,
        related_name='tags')
    image = models.ImageField(
        upload_to='food/images.',
        null=True,
        default=None)

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f"{self.name} от {self.author}"


class IngredientForRecipe(models.Model):
    """Ингридиент для рецепта."""
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Ингридиент для рецепта'
        verbose_name_plural = 'Ингридиентов для рецепта'

    def __str__(self):
        return f"{self.ingredient} в {self.recipe}"


class Favourites(models.Model):
    """Избранные товары."""
    user = models.ForeignKey(to=User,
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(to=Recipe,
                               on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"

    def __str__(self):
        return f"{self.user} сохранил {self.recipe}"
