from django.urls import path
from djoser.views import UserViewSet
from .views import MyAuthToken, Logout

urlpatterns = [
    path('',
         UserViewSet.as_view({'post': 'create'}),
         name='register'),
    path("set-password/",
         UserViewSet.as_view({"post": "set_password"}),
         name="set-password"),
    path('token/login/', MyAuthToken.as_view(), name='login'),
    path('token/logout/', Logout.as_view(), name='logout')
]
