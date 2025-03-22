from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Logbook, ParameterAnswer, Baseline, Suggestion, Treatment, Parameter, BlogEntry, BlogComment, BlogLike, EnumType, UserProfile
from .serializers import BlogEntrySerializer, BlogCommentSerializer, BlogLikeSerializer, UserSerializer,ParameterSerializer, ParameterSerializer, LogbookSerializer, RegisterSerializer, BaselineSerializer, SuggestionSerializer, EnumTypeSerializer, UserProfileSerializer

import random
import json

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserProfileView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id: int, format=None):
        try:
            userProfile = UserProfile.objects.get(user_id=user_id)
            return Response(UserProfileSerializer(userProfile).data, status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, user_id: int, format=None):
        # read the request body and create the entries
        reference = request.data["reference"]
        try:
            userProfile = UserProfile.objects.get(user_id=user_id)
            userProfile.reference_user_id = reference
            userProfile.save()
            return Response(status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, user_id: int, format=None):
        # read the request body and create the entries
        reference = request.data["reference"]
        refernceUser = User.objects.filter(id=reference).first()
        if not refernceUser:
            return Response({"error": "Reference user not found"}, status=status.HTTP_404_NOT_FOUND) 
        
        if UserProfile.objects.filter(user_id=user_id):
            userProfile = UserProfile.objects.get(user_id=user_id)
            userProfile.reference_user_id = reference
            userProfile.save()
            return Response(status=status.HTTP_200_OK)
        
        userProfile = UserProfile.objects.create(user_id=user_id, reference_user=refernceUser)
        userProfile.save()

        return Response(status=status.HTTP_201_CREATED)

# class UserProfileView(APIView):
#     authentication_classes = []
#     permission_classes = []

#     def get(self, request, user_id: int, format=None):
#         userProfile = UserProfile.objects.filter(user_id=user_id)
#         return Response(UserProfileSerializer(userProfile).data, status.HTTP_200_OK)
    
#     def put(self, request, user_id: int, format=None):
#         # read the request body and create the entries
#         reference = request.data["reference"]
#         userProfile = UserProfile.objects.filter(user_id=user_id)
#         userProfile.update(reference_user=reference)
#         userProfile.save()

#         return Response(status=status.HTTP_201_CREATED)
    
#     def post(self, request, user_id: int, format=None):
#         # read the request body and create the entries
#         reference = request.data["reference"]
#         refernceUser = User.objects.filter(id=reference)
#         if not refernceUser.exists():
#             return Response(status=status.HTTP_404_NOT_FOUND) 
#         userProfile = UserProfile.objects.create(user_id=user_id, reference_user=refernceUser.get())
#         userProfile.save()

#         return Response(status=status.HTTP_201_CREATED)

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

        response = algo.retLogs(user_id)

        # logbooks = Logbook.objects.filter(user_id=user_id)
        
        # response = []
        # for logbook in logbooks:
        #     response.append(LogbookSerializer(logbook).data)

        return Response(response, status.HTTP_200_OK)

    def post(self, request, user_id: int, format=None):
        is_passive = False
        if "is_auto_generated" in request.data:
            is_passive = request.data["is_auto_generated"]

        logbook = Logbook.objects.create(user_id=user_id, is_auto_generated=is_passive)
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
        
        if is_passive:
            treatment_id = algo.passiveTreatment(logbook.id)
            if treatment_id is None:
                return Response(status=status.HTTP_201_CREATED)
            
            suggestion = Suggestion.objects.create(
                logbook_entry=logbook,
                user_id=user_id,
                treatment_id=treatment_id
            )
            suggestion.save()
            return Response(SuggestionSerializer(suggestion).data, status.HTTP_200_OK)

        return Response(logbook.id, status=status.HTTP_201_CREATED)

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
    
class BaselineQuestionView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        parameters = Parameter.objects.filter(baselineQuestion=True)
        
        response = []
        for parameter in parameters:
            response.append(ParameterSerializer(parameter).data)

        return Response(response, status.HTTP_200_OK)

class ParameterGeneralView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        parameters = Parameter.objects.filter(user_id=None)
        
        response = []
        for parameter in parameters:
            response.append(ParameterSerializer(parameter).data)

        return Response(response, status.HTTP_200_OK)

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

class ParameterEditView(APIView):
    authentication_classes = []
    permission_classes = []

    def delete(self, request, user_id: int, parameter_id: int, format=None):
        param = Parameter.objects.filter(id=parameter_id)
        if param is None or not (param.exists()):
            return Response(status=status.HTTP_404_NOT_FOUND)
         
        param.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class EnumTypeView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, user_id: int, parameter_id: int, format=None):
        # read the request body and create the entries
        params = Parameter.objects.filter(user_id = user_id, id=parameter_id)
        if not params.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        display = request.data["display"]
        value = request.data["value"]
        enumType = EnumType.objects.create(display=display, value=value, parameter_id=parameter_id)
        enumType.save()

        return Response(status=status.HTTP_201_CREATED)
    
    def get(self, request, user_id: int, parameter_id: int, format=None):
        params = Parameter.objects.filter(user_id = user_id, id=parameter_id)
        if not params.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        enumTypes = EnumType.objects.filter(parameter_id=parameter_id)

        response = []
        for enumType in enumTypes:
            response.append(EnumTypeSerializer(enumType).data)

        return Response(response, status.HTTP_200_OK)
    
class EnumTypeGeneralView(APIView):
    def get(self, request, parameter_id: int, format=None):
        params = Parameter.objects.filter(user_id = None, id=parameter_id)
        if not params.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        enumTypes = EnumType.objects.filter(parameter_id=parameter_id)

        response = []
        for enumType in enumTypes:
            response.append(EnumTypeSerializer(enumType).data)

        return Response(response, status.HTTP_200_OK)
class BlogView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        blogentries = BlogEntry.objects.all()
        
        response = []
        for entry in blogentries:
            response.append(BlogEntrySerializer(entry).data)

        return Response(response, status.HTTP_200_OK)
    
class BlogSingleView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, user_id: int, format=None):
        # read the request body and create the entries
        title = request.data["title"]
        content = request.data["content"]
        # try:
        #     if len(content) > 1024:
        blogentry = BlogEntry.objects.create(user_id=user_id, title=title, content=content)
        blogentry.save()
        #     else:
        #         return Response(status=status.HTTP_400_BAD_REQUEST)
        # except:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)
    
class CommentView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id: int, blog_id: int, format=None):
        comments = BlogComment.objects.filter(blog_id = blog_id)
        
        response = []
        for comment in comments:
            response.append(BlogCommentSerializer(comment).data)

        return Response(response, status.HTTP_200_OK)

    def post(self, request, user_id: int, blog_id: int, format=None):
        content = request.data["content"]
        try:
            if len(content) < 1025:
                comment = BlogComment.objects.create(user_id=user_id, blog_id=blog_id, content=content)
                comment.save()
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)
    
class LikeView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id: int, blog_id: int, format=None):
        likes = BlogLike.objects.filter(blog_id = blog_id)
        
        response = []
        for like in likes:
            response.append(BlogLikeSerializer(like).data)


        return Response(len(response), status.HTTP_200_OK)

    def post(self, request, user_id: int, blog_id: int, format=None):
        try:
            if BlogLike.objects.filter(user_id=user_id, blog_id=blog_id).exists():
                like = BlogLike.objects.filter(user_id=user_id, blog_id=blog_id)
                like.delete()
            else:
                like = BlogLike.objects.create(user_id=user_id, blog_id=blog_id)
                like.save()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)
    
from . import algo
class SuggestionView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id: int, log_id: int, format=None):
        # First check if the logbook exists
        try:
            logbook = Logbook.objects.get(id=log_id, user_id=user_id)
        except Logbook.DoesNotExist:
            return Response({"error": "Logbook not found"}, status=status.HTTP_404_NOT_FOUND)

        suggestions = Suggestion.objects.filter(user_id=user_id, logbook_entry_id=log_id)

        # no suggestion, generate one with algo
        if suggestions is None or len(suggestions) == 0:
            """# get all parameters
            parameters = list(Parameter.objects.filter(Q(user_id=user_id) | Q(user_id=None)))
            # get history suggestions for user
            suggestions = Suggestion.objects.filter(user_id=user_id)
            # get grouped parameter answers
            grouped_parameter_answers = []

            for suggestion in suggestions:
                vec = [None for _ in range(len(parameters) + 2)]
                vec[0] = suggestion.treatment.id
                vec[1] = suggestion.effectiveness
                for answer in suggestion.logbook_entry.answers.all():
                    vec[answer.parameter_id + 2] = answer.normalised_answer
                grouped_parameter_answers.append(vec)

            # Get current status aka logbook answer
            current_logbook = Logbook.objects.filter(user_id=user_id, id=log_id)
            if current_logbook is None or len(current_logbook) == 0:
                return Response("Not found", status.HTTP_404_NOT_FOUND)
            current_logbook = current_logbook[0]
            current_logbook_answers = [None for _ in range(len(parameters))]
            for answer in current_logbook.answers.all():
                current_logbook_answers[answer.parameter_id] = answer.normalised_answer
            
            # get the suggestions
            score = algo.treatmentoptions(grouped_parameter_answers, [1 for _ in range(len(current_logbook_answers))],current_logbook_answers)
            """
            refUser = UserProfile.objects.all().exclude(user_id=user_id)
            suggestions = algo.rankFromDBwithRef(log_id,refUser,20)

            
            if len(suggestions) == 0:
                sug = Suggestion.objects.create(
                        logbook_entry_id=log_id,
                        user_id=user_id,
                        treatment_id=random.choice(Treatment.objects.all()).id,
                    )
                sug.save()
                return Response(SuggestionSerializer(sug).data, status.HTTP_200_OK)

            # Pick suggestion by randomization with weights
            sum_score = sum([suggestion[1] for suggestion in suggestions])
            
            if sum_score == 0:
                # If all scores are zero, use equal weights
                weights = [1.0 / len(suggestions)] * len(suggestions)
            else:
                # normalize weights
                weights = [s[1] / sum_score for s in suggestions]
                
            chosen_suggestion = random.choices(suggestions, weights=weights)
            # save the suggestion
            sug = Suggestion.objects.create(
                logbook_entry_id=log_id,
                user_id=user_id,
                treatment_id=chosen_suggestion[0][0],
            )
            sug.save()
            return Response(SuggestionSerializer(sug).data, status.HTTP_200_OK)

        return Response(SuggestionSerializer(suggestions[0]).data, status.HTTP_200_OK)

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

        suggestion.perceived_effectiveness = request.data["perceived_effectiveness"]
        suggestion.effectiveness = request.data["effectiveness"]
        suggestion.save()

        return Response({
            "id": suggestion.id,
            "logbook_entry": suggestion.logbook_entry.id,
            "user": suggestion.user.id,
            "treatment": suggestion.treatment.id,
            "perceived_effectiveness": suggestion.perceived_effectiveness,
            "effectiveness": suggestion.effectiveness
        }, status.HTTP_200_OK)
    
class MetricActiveView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id: int, format=None):
        bestTreatments = algo.statisticsOverall(user_id)
        if len(bestTreatments) > 0:
            return Response(bestTreatments, status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_201_CREATED)
        
class MetricPassiveView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id: int, format=None):
        bestTreatments = algo.statisticsPassive(user_id)
        if len(bestTreatments) > 0:
            return Response(bestTreatments, status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_201_CREATED)
        
class MetricParameterView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id: int, parameter_id: int, norm: int, format=None):
        bestTreatments = algo.statisticsCustom(user_id, parameter_id, norm)
        if len(bestTreatments) > 0:
            return Response(bestTreatments, status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_201_CREATED)

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

class UserView(APIView):
    def get(self, request, user_id: int, format=None):
        user = User.objects.filter(id=user_id)
        if user is None or len(user) == 0:
            return Response("Not found", status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user[0]).data, status.HTTP_200_OK)

class UserTokenView(APIView):
    def get(self, request, format=None):
        if not request.user or not request.user.id:
            return Response("Not found", status.HTTP_404_NOT_FOUND)
        
        user = User.objects.filter(id=request.user.id)
        if user is None or len(user) == 0:
            return Response("Not found", status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user[0]).data, status.HTTP_200_OK)
