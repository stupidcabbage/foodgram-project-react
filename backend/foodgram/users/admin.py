from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_filter = ["email", "username"]
