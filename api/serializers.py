from django.contrib.auth.models import User
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
    entries = serializers.SerializerMethodField()
    class Meta:
        model = Logbook
        fields = ['id', 'time', 'entries']
    def get_entries(self, obj):
        entries = ParameterAnswer.objects.filter(logbook_entry=obj)
        return ParameterAnswerSerializer(entries, many=True).data
    
    def update(self, instance, validated_data):
        # update time and entries which is identified by parameter_id
        entries = validated_data.pop('entries')
        instance.time = validated_data.get('time', instance.time)
        instance.save()
        # update the entries
        for entry in entries:
            if not ParameterAnswer.objects.filter(parameter_id=entry["parameter_id"], logbook_entry=instance).exists():
                # create a new entry
                ParameterAnswer.objects.create(
                    parameter_id=entry["parameter"],
                    answer=entry["answer"],
                    normalised_answer=entry["normalised_answer"],
                    logbook_entry=instance
                ).save()
            else:
                # update the entry
                entry = ParameterAnswer.objects.filter(parameter_id=entry["parameter_id"], logbook_entry=instance)[0]
                entry.answer = entry["answer"]
                entry.normalised_answer = entry["normalised_answer"]
                entry.save()


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

        fields = ['url', 'username', 'email', 'is_staff']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user