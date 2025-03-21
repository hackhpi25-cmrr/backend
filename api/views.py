from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Logbook, ParameterAnswer
from .serializers import UserSerializer, ParameterAnswerSerializer, LogbookSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LogbookViewSingle(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id: int, log_id: int, format=None):
        logbook = Logbook.objects.filter(user_id=user_id, id=log_id)
        if logbook is None or len(logbook) == 0:
            return Response("Not found", status.HTTP_404_NOT_FOUND)

        return Response(
            LogbookSerializer(logbook[0]).data, status.HTTP_200_OK
        )
        

class LogbookView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id: int, format=None):
        logbooks = Logbook.objects.filter(user_id=user_id)
        if logbooks is None or len(logbooks) == 0:
            return Response("Not found", status.HTTP_404_NOT_FOUND)
        

        response = []
        for logbook in logbooks:
            response.append(LogbookSerializer(logbook).data)

        return Response(response, status.HTTP_200_OK)

    def post(self, request, user_id: int, format=None):
        logbook = Logbook.objects.create(user_id=user_id)
        logbook.save()

        # read the request body and create the entries
        entries = request.data["parameters"]
        for entry in entries:
            ParameterAnswer.objects.create(
                parameter_id=entry["parameter_id"],
                answer=entry["answer"],
                normalised_answer=entry["normalised_answer"],
                logbook_entry=logbook
            ).save()

        return Response({
            "id": logbook.id,
            "time": logbook.time
        }, status.HTTP_201_CREATED)
    
        

class AuthTestView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, user_id: int, log_id: int, request, format=None):
        return Response("You are authenticated!", status.HTTP_200_OK)