from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Parameter(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_parameters", null=True, blank=True)
    name = models.CharField(max_length=512)

    class Type(models.TextChoices):
        ENUM = "Enum"
        BOOLEAN = "Boolean"
        NUMBER = "Number"

    parameter_type = models.CharField(max_length=32, choices=Type.choices)
    passive = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class EnumType(models.Model):

    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name="enumtypes")
    display = models.CharField(max_length=128)
    value = models.IntegerField()

    def __str__(self):
        return self.display

class Logbook(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="logbook_entries")
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}: {self.time}"

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

    def __str__(self):
        return f"{self.parameter.name}: {self.answer}"

class Treatment(models.Model):
    
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Suggestion(models.Model):

    logbook_entry  = models.OneToOneField(Logbook, on_delete=models.CASCADE, related_name="suggestion")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="suggestions")
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    perceived_effectiveness = models.FloatField( # perceived by user
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ],
        null=True,
        blank=True,
    )
    effectiveness = models.FloatField( # calculated
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ],
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}: {self.treatment.name}"

class BaselineQuestion(models.Model):

    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Baseline(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="baselines")
    question = models.ForeignKey(BaselineQuestion, on_delete=models.CASCADE)
    normalised_answer = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ]
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}: {self.question.name}"

class BlogEntry(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blog_entries")
    title = models.CharField(max_length=128)
    content = models.CharField(max_length=1024)

    def __str__(self):
        return self.title
    

class BlogComment(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    blog = models.ForeignKey(BlogEntry, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=1024)

    def __str__(self):
        return self.content

class BlogLike(models.Model):

    blog = models.ForeignKey(BlogEntry, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}: {self.blog.title}"
