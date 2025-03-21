from django.contrib import admin

# Register your models here.
from .models import EnumType, Logbook, Parameter, ParameterAnswer, Suggestion, Treatment
admin.site.register(EnumType)
admin.site.register(Logbook)
admin.site.register(Parameter)
admin.site.register(ParameterAnswer)
admin.site.register(Suggestion)
admin.site.register(Treatment)

