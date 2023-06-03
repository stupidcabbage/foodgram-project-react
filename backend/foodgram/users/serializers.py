from djoser.serializers import UserCreateSerializer
from .models import User


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password',)
        read_only_fields = ('id',)
