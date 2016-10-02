from rest_framework import serializers
from .models import Player


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('__all__',)
