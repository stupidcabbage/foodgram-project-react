from django.contrib import admin
from food.models import Tag, Ingridient, Recipe


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "slug", "colour"]
    list_filter = ["id", "name", "colour"]


@admin.register(Ingridient)
class IngridientAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    pass
