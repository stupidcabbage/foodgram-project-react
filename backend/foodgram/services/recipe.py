from food.models import Recipe
from users.models import User


def get_count_recipe_filtering_author(author: User) -> Recipe:
    """Возвращает кол-во рецептов, отфильтровав по автору."""
    return Recipe.objects.filter(author=author).count()


def filter_by_author(author: User) -> Recipe:
    """Возвращает рецепты, отфильтровав по автору."""
    return Recipe.objects.filter(author=author)


def create_recipe(data) -> Recipe:
    """Создает рецепт."""
    return Recipe.objects.create(**data)


def get_all_recipes() -> Recipe:
    """Возвращает все рецепты."""
    return Recipe.objects.all()
