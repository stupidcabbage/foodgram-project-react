from food.models import Tag


def get_all_tags() -> Tag:
    """Возвращает все существующие тэги."""
    return Tag.objects.all()
