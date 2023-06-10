from django.contrib import admin
from food.models import Ingridient, IngridientForRecipe, Recipe, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "slug", "colour"]
    list_filter = ["id", "name", "colour"]


@admin.register(Ingridient)
class IngridientAdmin(admin.ModelAdmin):
    pass


class IngridientForRecipeInline(admin.TabularInline):
    model = IngridientForRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngridientForRecipeInline]
