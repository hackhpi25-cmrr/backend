from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LogView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, user_id: int, log_id: int, request, format=None):
        return Response("You are authenticated!", status.HTTP_200_OK)
    
class AuthTestView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        return Response("hello", status.HTTP_200_OK)