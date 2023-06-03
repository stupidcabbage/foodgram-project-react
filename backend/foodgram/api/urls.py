from django.urls import path, include
from djoser.views import UserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    path('', UserViewSet.as_view({'post': 'create'}), name='register'),
]
