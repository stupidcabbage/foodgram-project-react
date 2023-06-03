from django.urls import path
from djoser.views import UserViewSet
from .views import EmailTokenObtainPairView, BlacklistRefreshView

urlpatterns = [
    path('',
         UserViewSet.as_view({'post': 'create'}),
         name='register'),
    path("set-password/",
         UserViewSet.as_view({"post": "set_password"}),
         name="set-password"),
    path('token/login/',
         EmailTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/logout/', BlacklistRefreshView.as_view(), name='logout')
]
