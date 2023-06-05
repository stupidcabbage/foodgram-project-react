from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from .views import LogoutToken, MyAuthToken

router_v1 = DefaultRouter()
router_v1.register('', UserViewSet, 'user')


urlpatterns = [
    path("set-password/",
         UserViewSet.as_view({"post": "set_password"}),
         name="set_password"),
    path('token/login/', MyAuthToken.as_view(), name='login'),
    path('token/logout/', LogoutToken.as_view(), name='logout'),
    path('', include((router_v1.urls, 'routers'), namespace='routers'),)
]
