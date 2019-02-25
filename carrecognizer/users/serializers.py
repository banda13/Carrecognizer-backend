from rest_framework import serializers

from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'is_active', 'date_joined', 'first_name', 'last_name', 'last_login') # TODO serialzer permissions!