from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from .views import LogoutToken, MyAuthToken, TagViewSet, IngridientViewSet, RecipeViewSet

router_v1 = DefaultRouter()
router_v1.register(r"users", UserViewSet, "user")
router_v1.register(r"tags", TagViewSet, "tags")
router_v1.register(r"ingridients", IngridientViewSet, "ingridients")
router_v1.register(r"recipes", RecipeViewSet, "recipes")


urlpatterns = [
    path("users/set-password/",
         UserViewSet.as_view({"post": "set_password"}),
         name="set_password"),
    path("users/token/login/", MyAuthToken.as_view(), name="login"),
    path("users/token/logout/", LogoutToken.as_view(), name="logout"),
    path("", include((router_v1.urls, "routers"), namespace="routers"),)
]
