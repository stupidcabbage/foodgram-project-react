from django.contrib import admin
from food.models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'colour']
    list_filter = ['id', 'name', 'colour']
