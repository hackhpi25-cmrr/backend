from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Parameter(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_parameters", null=True)
    name = models.CharField(max_length=128)

    class Type(models.TextChoices):
        ENUM = "Enum"
        BOOLEAN = "Boolean"
        NUMBER = "Number"

    type = models.CharField(max_length=32, choices=Type.choices)

class EnumType(models.Model):

    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name="enumtypes")
    display = models.CharField(max_length=128)
    value = models.IntegerField()

class Logbook(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="logbook_entries")
    time = models.DateTimeField(auto_now_add=True)

class ParameterAnswer(models.Model):

    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE)
    answer = models.IntegerField()
    normalised_answer = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ]
    )
    logbook_entry = models.ForeignKey(Logbook, on_delete=models.CASCADE, related_name="answers")

class Treatment(models.Model):
    
    name = models.CharField(max_length=128)

class Suggestion(models.Model):

    lookentry = models.ForeignKey(Logbook, on_delete=models.CASCADE, related_name="suggestion")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="suggestions")
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    perceived_effectiveness = models.FloatField( # perceived by user
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ]
    )
    effectiveness = models.FloatField( # calculated
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ]
    )

class BaselineQuestion(models.Model):

    name = models.CharField(max_length=128)

class Baseline(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_parameters")
    question = models.ForeignKey(BaselineQuestion, on_delete=models.CASCADE, related_name="user_parameters")
    normalised_answer = models.FloatField( # perceived by user
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ]
    )