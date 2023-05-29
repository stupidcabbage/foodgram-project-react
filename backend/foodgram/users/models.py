from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
import re


class User(AbstractUser):
    username = models.CharField(
        'Псевдоним',
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(regex=re.compile(r"^[\w.@+-]+\Z"),
                           message='Проверьте правильность написания никнейма')
        ])
    last_name = models.CharField(
        'Фамилия пользователя',
        max_length=150)
    first_name = models.CharField(
        'Имя пользователя',
        max_length=150)
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True)

    def __str__(self):
        return f'{self.username}: {self.email}'
