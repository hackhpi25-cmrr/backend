from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Logbook, ParameterAnswer, Baseline, Suggestion, Treatment, Parameter
from .serializers import UserSerializer, ParameterAnswerSerializer, LogbookSerializer, RegisterSerializer, BaselineSerializer, SuggestionSerializer

import random

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
    
    def put(self, request, user_id: int, log_id: int, format=None):
        logbook = Logbook.objects.filter(user_id=user_id, id=log_id)
        if logbook is None or len(logbook) == 0:
            return Response("Not found", status.HTTP_404_NOT_FOUND)
        
        logbook = logbook[0]
        if logbook.user.id != user_id:
            return Response("Not found", status.HTTP_404_NOT_FOUND)

        new_serialzier = LogbookSerializer(data=request.data) 
        if not new_serialzier.is_valid():
            return Response("Invalid data", status.HTTP_400_BAD_REQUEST)
        
        new_serialzier.update(logbook, request.data["entries"])

        return Response({
            "id": logbook.id,
            "time": logbook.time
        }, status.HTTP_200_OK)

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
        entries = request.data["entries"]
        for entry in entries:
            ParameterAnswer.objects.create(
                parameter_id=entry["parameter_id"],
                answer=entry["answer"],
                normalised_answer=entry["normalised_answer"],
                logbook_entry=logbook
            ).save()

        return Response(status=status.HTTP_201_CREATED)
    
class ParameterView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id: int, format=None):
        parameters = Parameter.objects.filter(user_id=user_id)
        
        response = []
        for parameter in parameters:
            response.append(ParameterSerializer(parameter).data)

        return Response(response, status.HTTP_200_OK)

    def post(self, request, user_id: int, format=None):
        # read the request body and create the entries
        name = request.data["name"]
        param_type = request.data["type"]
        parameter = Parameter.objects.create(user_id=user_id, name=name, parameter_type=param_type)
        parameter.save()

        return Response(status=status.HTTP_201_CREATED)

class BaselineView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id: int, format=None):
        baselines = Baseline.objects.filter(user_id=user_id)
        if baselines is None or len(baselines) == 0:
            return Response("Not found", status.HTTP_404_NOT_FOUND)
        
        response = []
        for baseline in baselines:
            response.append(BaselineSerializer(baseline).data)

        return Response(response, status.HTTP_200_OK)

    def post(self, request, user_id: int, format=None):
        # read the request body and create the entries
        entries = request.data["entries"]
        for entry in entries:
            Baseline.objects.create(
                question_id=entry["question_id"],
                normalised_answer=entry["normalised_answer"],
                user_id=user_id
            ).save()

        return Response(status=status.HTTP_201_CREATED)

class ParameterEditView(APIView):
    authentication_classes = []
    permission_classes = []

    def delete(self, request, user_id: int, parameter_id: int, format=None):
        param = Parameter.objects.filter(id=parameter_id)
        breakpoint()
        if param is None or not (param.exists()):
            return Response(status=status.HTTP_404_NOT_FOUND)
         
        param.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
import algo

class SuggestionView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id: int, log_id: KeyboardInterrupt, format=None):
        suggestions = Suggestion.objects.filter(user_id=user_id, logbook_entry_id=log_id)

        # no suggestion, generate one with algo
        if suggestions is None or len(suggestions) == 0:
            # get all parameters
            parameters = Parameter.objects.filter(Q(user_id=user_id) | Q(user_id=None))
            parameters.append(Parameter.objects.filter(user_id=user_id))
            # get history suggestions for user
            suggestions = Suggestion.objects.filter(user_id=user_id)
            # get grouped parameter answers
            grouped_parameter_answers = []

            for suggestion in suggestions:
                vec = [None * (len(parameters) + 2)]
                vec[0] = suggestion.treatment.id
                vec[1] = suggestion.effectiveness
                for answer in suggestion.logbook_entry.answers:
                    vec[answer.parameter_id + 2] = answer.normalised_answer
                grouped_parameter_answers.append(vec)

            # Get current status aka logbook answer
            current_logbook = Logbook.objects.filter(user_id=user_id, id=log_id)
            if current_logbook is None or len(current_logbook) == 0:
                return Response("Not found", status.HTTP_404_NOT_FOUND)
            current_logbook = current_logbook[0]
            current_logbook_answers = [None * len(parameters)]
            for answer in current_logbook.answers:
                current_logbook_answers[answer.parameter_id] = answer.normalised_answer
            
            # get the suggestions
            score = algo.treatmentoptions(grouped_parameter_answers, [1 for _ in range(len(current_logbook_answers))],current_logbook_answers)
            suggestions = algo.rankTreatmentByUse(score)
            # Pick suggestion by randomization with weights
            sum_score = sum([suggestion[1] for suggestion in suggestions])
            for suggestion in suggestions:
                suggestion[1] /= sum_score
            chosen_suggestion = random.choices(suggestions, [s[1] for s in range(len(suggestions))])
            # save the suggestion
            Suggestion.objects.create(
                logbook_entry_id=log_id,
                user_id=user_id,
                treatment_id=chosen_suggestion[0][0],
            ).save()
            return Response(chosen_suggestion[0], status.HTTP_200_OK)

        return Response(suggestions[0], status.HTTP_200_OK)

class SuggestionEditView(APIView):
    authentication_classes = []
    permission_classes = []

    def put(self, request, user_id: int, log_id: int, suggestion_id: int, format=None):
        suggestion = Suggestion.objects.filter(user_id=user_id, logbook_entry_id=log_id, id=suggestion_id)
        if suggestion is None or len(suggestion) == 0:
            return Response("Not found", status.HTTP_404_NOT_FOUND)
        
        suggestion = suggestion[0]
        if suggestion.user.id != user_id:
            return Response("Not found", status.HTTP_404_NOT_FOUND)

        new_serialzier = SuggestionSerializer(data=request.data) 
        if not new_serialzier.is_valid():
            return Response("Invalid data", status.HTTP_400_BAD_REQUEST)
        
        new_serialzier.update(suggestion, request.data)

        return Response({
            "id": suggestion.id,
            "logbook_entry": suggestion.logbook_entry.id,
            "user": suggestion.user.id,
            "treatment": suggestion.treatment.id,
            "perceived_effectiveness": suggestion.perceived_effectiveness,
            "effectiveness": suggestion.effectiveness
        }, status.HTTP_200_OK)

class AuthTestView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, user_id: int, log_id: int, request, format=None):
        return Response("You are authenticated!", status.HTTP_200_OK)
    def get(self, request, format=None):
        return Response("hello", status.HTTP_200_OK)
    
class RegisterView(APIView):
    def post(self, request):
        print(request.data)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Created user successfully"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)