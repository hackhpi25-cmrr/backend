from django.contrib.auth.models import Group, User
from rest_framework import serializers
from .models import EnumType

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

class EnumTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnumType
        fields = ['id', 'display', 'value']
