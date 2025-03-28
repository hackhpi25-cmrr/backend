from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (
    Parameter,
    EnumType,
    Logbook,
    ParameterAnswer,
    Treatment,
    Suggestion,
    Baseline,
    BlogEntry,
    BlogComment,
    BlogLike,
    UserProfile
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'is_staff', 'date_joined']

class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = '__all__'

class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = '__all__'


class EnumTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnumType
        fields = ['id', 'parameter', 'display', 'value']


class LogbookSerializer(serializers.ModelSerializer):
    entries = serializers.SerializerMethodField()
    class Meta:
        model = Logbook
        fields = ['id', 'time', 'entries', 'weight']
    def get_entries(self, obj):
        entries = ParameterAnswer.objects.filter(logbook_entry=obj)
        return ParameterAnswerSerializer(entries, many=True).data

    def update(self, instance, entries):
        # update the entries
        for entry in entries:
            if not ParameterAnswer.objects.filter(parameter_id=entry["parameter_id"], logbook_entry=instance).exists():
                # create a new entry
                ParameterAnswer.objects.create(
                    parameter_id=entry.parameter_id,
                    answer=entry.answer,
                    normalised_answer=entry.normalised_answer,
                    logbook_entry=instance
                ).save()
            else:
                # update the entry
                old_entry = ParameterAnswer.objects.filter(parameter_id=entry["parameter_id"], logbook_entry=instance)[0]
                old_entry.answer = entry.answer
                old_entry.normalised_answer = entry.normalised_answer
                old_entry.save()


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


class BaselineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Baseline
        fields = ['id', 'user', 'question', 'normalised_answer']

class BlogEntrySerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogEntry 
        fields = '__all__'
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_comments_count(self, obj):
        return obj.comments.count()

class BlogCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogComment 
        fields = '__all__'

class BlogLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogLike 
        fields = '__all__'


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