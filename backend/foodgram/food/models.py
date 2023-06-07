import re

from django.db import models
from users.models import User
from django.core.validators import RegexValidator


class Ingridient(models.Model):
    name = models.CharField(
        "Название",
        unique=True,
        max_length=200)
    measurement_unit = models.CharField("Мера измерения", max_length=200)

    def __str__(self):
        return f"{self.name} в {self.measurement_unit}"


class Tag(models.Model):
    COLOURS = [
        ("#E26C2D", "orange"),
        ("#49B64E", "green"),
        ("#8775fD2", "purple")
    ]

    name = models.CharField("Название",
                            max_length=200,
                            unique=True)
    colour = models.CharField("Цвет",
                              max_length=200,
                              unique=True,
                              choices=COLOURS)
    slug = models.SlugField(
        "Тэг",
        unique=True,
        max_length=200,
        validators=[
            RegexValidator(regex=re.compile(r"^[-a-zA-Z0-9_]+$"),
                           message="Проверьте правильность написания никнейма")
            ])

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        verbose_name="Автор публикации",
        to=User,
        on_delete=models.CASCADE,
        related_name="author")
    name = models.CharField(
        "Название",
        max_length=200)
    text = models.TextField(
        "Описание")
    cooking_time = models.IntegerField(
        "Время приготовления")
    ingridients = models.ManyToManyField(
        verbose_name="Ингридиенты",
        to=Ingridient,
        related_name="ingridients")
    tag = models.IntegerField()
