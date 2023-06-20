from django.contrib import admin

from food.models import Ingredient, IngredientForRecipe, Recipe, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "slug", "color"]
    list_filter = ["id", "name", "color"]


@admin.register(Ingredient)
class IngridientAdmin(admin.ModelAdmin):
    list_display = ["name", "measurement_unit"]
    list_filter = ["measurement_unit"]


class IngridientForRecipeInline(admin.TabularInline):
    model = IngredientForRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["author", "name", "text", "cooking_time"]
    inlines = [IngridientForRecipeInline]
