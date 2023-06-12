from food.models import Favorites, Recipe
from users.models import User


def is_favorite_exists(recipe: Recipe, user=User) -> bool:
    """Возвращает результат проверки на существование в любимом."""
    return Favorites.objects.filter(recipe=recipe, user=user).exists()
