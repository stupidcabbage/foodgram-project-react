import re

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        "Псевдоним",
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(regex=re.compile(r"^[\w.@+-]+\Z"),
                           message="Проверьте правильность написания никнейма")
        ])
    last_name = models.CharField(
        "Фамилия пользователя",
        max_length=150)
    first_name = models.CharField(
        "Имя пользователя",
        max_length=150)
    email = models.EmailField(
        "Электронная почта",
        max_length=254,
        unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        ordering = ("id",)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.username}: {self.email}"


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='followers',
                             verbose_name='Подписчик')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='subscriber',
                               verbose_name='Подписка на')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
