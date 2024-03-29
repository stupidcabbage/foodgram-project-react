from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from api.views import IngridientViewSet, RecipeViewSet, TagViewSet
from users.views import AuthToken, CustomUserViewSet, LogoutToken

router_v1 = DefaultRouter()
router_v1.register(r"users", CustomUserViewSet, "user")
router_v1.register(r"tags", TagViewSet, "tags")
router_v1.register(r"ingredients", IngridientViewSet, "ingredients")
router_v1.register(r"recipes", RecipeViewSet, "recipes")


urlpatterns = [
    path("users/set-password/",
         UserViewSet.as_view({"post": "set_password"}),
         name="set_password"),
    path("auth/token/login/", AuthToken.as_view(), name="login"),
    path("auth/token/logout/", LogoutToken.as_view(), name="logout"),
    path("", include((router_v1.urls, "routers"), namespace="routers"),)
]
