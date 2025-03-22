from django.contrib import admin

# Register your models here.
from .models import EnumType, Logbook, Parameter, ParameterAnswer, Suggestion, Treatment, Baseline, BlogEntry, BlogComment, BlogLike, UserProfile
admin.site.register(EnumType)
admin.site.register(Logbook)
admin.site.register(Parameter)
admin.site.register(ParameterAnswer)
admin.site.register(Suggestion)
admin.site.register(Treatment)
admin.site.register(Baseline)
admin.site.register(BlogEntry)
admin.site.register(BlogComment)
admin.site.register(BlogLike)
admin.site.register(UserProfile)
