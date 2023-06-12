from food.models import Recipe
from users.models import User


def is_exists(user: User, recipe: Recipe, model):
    """Возвращает результат проверки на существование в БД."""
    return model.objects.filter(user=user, recipe=recipe).exists()


def create(user: User, recipe: Recipe, model):
    """Создает модель объекта"""
    return model.objects.create(user=user, recipe=recipe)


def delete(user: User, recipe: Recipe, model):
    """Удаляет модель объекта."""
    return model.objects.filter(user=user, recipe=recipe).delete()
