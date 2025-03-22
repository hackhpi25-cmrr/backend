"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

import api.views as apiViews

router = routers.DefaultRouter()
router.register(r'users', apiViews.UserViewSet)

urlpatterns = [ 
    #path('', include(router.urls)),
    path('amiauth', apiViews.AuthTestView.as_view()),
    # User
    path('users/<int:user_id>', apiViews.UserView.as_view()),
    path('users', apiViews.UserTokenView.as_view()),
    path('users/<int:user_id>/reference', apiViews.UserProfileView.as_view()),
    # Logbook
    path('users/<int:user_id>/logs/<int:log_id>', apiViews.LogbookViewSingle.as_view()),
    path('users/<int:user_id>/logs', apiViews.LogbookView.as_view()),
    # Baseline
    path('users/<int:user_id>/baseline', apiViews.BaselineView.as_view()),
    path('basequestions', apiViews.BaselineQuestionView.as_view()),
    # Parameters
    path('users/<int:user_id>/parameters', apiViews.ParameterView.as_view()),
    path('parameters', apiViews.ParameterGeneralView.as_view()),
    path('parameter/<int:parameter_id>/enumtype', apiViews.EnumTypeGeneralView.as_view()),
    path('users/<int:user_id>/parameter/<int:parameter_id>', apiViews.ParameterEditView.as_view()),
    path('users/<int:user_id>/parameter/<int:parameter_id>/enumtype', apiViews.EnumTypeView.as_view()),
    # Suggestion
    path('users/<int:user_id>/logs/<int:log_id>/suggestion', apiViews.SuggestionView.as_view()),
    path('users/<int:user_id>/logs/<int:log_id>/suggestions/<int:suggestion_id>', apiViews.SuggestionEditView.as_view()),
    # Blog
    path('users/<int:user_id>/blog', apiViews.BlogSingleView.as_view()),
    path('blogentries', apiViews.BlogView.as_view()),
    path('users/<int:user_id>/blog/<int:blog_id>/comment', apiViews.CommentView.as_view()),
    path('users/<int:user_id>/blog/<int:blog_id>/like', apiViews.LikeView.as_view()),

    path('register', apiViews.RegisterView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
