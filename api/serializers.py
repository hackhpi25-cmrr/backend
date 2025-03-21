from django.contrib.auth.models import Group, User
from rest_framework import serializers
from .models import (
    Parameter,
    EnumType,
    Logbook,
    ParameterAnswer,
    Treatment,
    Suggestion,
    BaselineQuestion,
    Baseline
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_staff', 'date_joined']

class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ['id', 'user', 'name', 'type']


class EnumTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnumType
        fields = ['id', 'parameter', 'display', 'value']


class LogbookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logbook
        fields = ['id', 'user', 'time']


class ParameterAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParameterAnswer
        fields = ['id', 'parameter', 'answer', 'normalised_answer', 'logbook_entry']


class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatment
        fields = ['id', 'name']


class SuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suggestion
        fields = ['id', 'logbook_entry', 'user', 'treatment', 'perceived_effectiveness', 'effectiveness']


class BaselineQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaselineQuestion
        fields = ['id', 'name']


class BaselineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Baseline
        fields = ['id', 'user', 'question', 'normalised_answer']
