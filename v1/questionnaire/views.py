
from rest_framework import generics
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string

from base.views import IdDecodeModelViewSet
from base import session
from base import response
from base import exceptions
from utilities.functions import decode
from utilities import email

from v1.accounts.authentication import ValidationTokenAuthentication

from v1.questionnaire import models as question_models
from v1.questionnaire import serializers as question_serializers
from v1.questionnaire import filters as question_filters
from v1.questionnaire import constants as question_consts


class QuestionnaireViewSet(IdDecodeModelViewSet):
    """
    Api used to create,list,retrieve,update and delete questionnaire.
    """
    filterset_class = question_filters.QuestionnaireFilter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'submitter',]
    serializer_class = question_serializers.QuestionnaireSerializer
    
    def get_queryset(self):
        """
        Return questionnaires of current node.
        """
        questionnaires = question_models.Questionnaire.objects.filter(
            owner=session.get_current_node(),is_deleted=False
            ).order_by('-created_on')
        return questionnaires
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete overrided to make the delete boolean true.
        """
        questionnaire = self.get_object()
        questionnaire.is_deleted = True
        questionnaire.save()
        return response.SuccessResponse(_(
            "Questionnaire deleted successfully"))
    

class QuestionnaireApproveView(generics.UpdateAPIView):
    """
    Api to approve questionnaire.
    """
    def get_object(self):
        """
        Return questionnaires of current node.
        """
        try:
            questionnaire = question_models.Questionnaire.objects.get(
                id=self.kwargs['pk'],
                owner=session.get_current_node(),is_deleted=False
                )
        except:
            raise exceptions.NotFound(_(
                'Questionnaire is not found or already approved'))
        return questionnaire
    
    def update(self, request, *args, **kwargs):
        """
        Update override to change status of the questionnaire.
        """
        questionnaire = self.get_object()
        questionnaire.status = question_consts.QuestionnaireStatus.APPROVED
        questionnaire.save()
        return response.SuccessResponse(_("Questionnaire approved."))


class QuestionnaireSubmitterListView(generics.ListAPIView):
    """
    Return Questionnaire submitters names.
    """
    filter_backends = [filters.SearchFilter,]
    search_fields = ['submitter',]

    def get_queryset(self):
        """
        Return questionnaires of current node.
        """
        questionnaires = question_models.Questionnaire.objects.filter(
            owner=session.get_current_node(),is_deleted=False,
            ).exclude(submitter=None)
        return questionnaires
    
    def list(self, request, *args, **kwargs):
        """
        Return only unique submitters of questionnaires
        """
        submitters = self.filter_queryset(self.get_queryset()
            ).order_by('submitter').distinct('submitter').values(
                'submitter')
        return response.SuccessResponse(list(submitters),default_data=[])


class QuestionViewSet(IdDecodeModelViewSet):
    """
    Api used to create,list,update and delete questions.
    """

    filterset_class = question_filters.QuestionFilter
    serializer_class = question_serializers.QuestionSerializer
    
    def get_queryset(self):
        """
        Return questions of current node.
        """
        questions = question_models.Question.objects.filter(
            questionnaire__owner=session.get_current_node(), 
            is_deleted=False
            ).order_by('id')
        return questions
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete overrided to make the delete boolean true.
        """
        question = self.get_object()
        question.is_deleted = True
        question.save()
        questionnaire = question.questionnaire
        if questionnaire.all_questions_answered():
            questionnaire.answer_generation_complete()
        data = {
            "questionnaire_status": questionnaire.status
        }
        return response.SuccessResponse(data,_(
            "Question deleted successfully"))


class AnswerCreateUpdateView(
        generics.CreateAPIView,
        generics.UpdateAPIView):
    """
    Api to create and update answer.
    """
    serializer_class = question_serializers.AnswerSerializer

    def get_object(self):
        """
        Return answer of specific question.
        """
        try:
            answer = question_models.Answer.objects.get(
                id=self.kwargs['id'],question__id=self.kwargs['pk'])
        except:
            raise exceptions.NotFound(_("Answer does not exist"))
        return answer


class PublicQuestionnaireView(generics.RetrieveAPIView):
    """
    Api to show questionnaire info in publically.
    """
    authentication_classes = [ValidationTokenAuthentication,]
    permission_classes = []
    serializer_class = question_serializers.PublicQuestionnaireSerializer

    def get_object(self):
        """
        Return questionnaires of current node.
        """
        try:
            token = self.request.token
            questionnaire = question_models.Questionnaire.objects.get(
                id=self.kwargs['pk'], is_deleted=False
                )
        except:
            raise exceptions.NotFound(_(
                'Questionnaire does not exist'))
        if token.has_notification() and token.notification.event != questionnaire:
            raise exceptions.BadRequest(
                _("Don't have the questionnaire access."))
        return questionnaire


class ShareQuestionnaire(generics.UpdateAPIView):
    """
    Api to share questionnaire to specific emails.
    """

    def get_object(self):
        """
        Return questionnaires of current node.
        """
        try:
            questionnaire = question_models.Questionnaire.objects.get(
                id=self.kwargs['pk'], owner=session.get_current_node(),
                is_deleted=False
                )
        except:
            raise exceptions.NotFound(_(
                'Questionnaire does not exist'))
        return questionnaire
    
    def update(self, request, *args, **kwargs):
        """
        Update Overrided to send email to given users.
        """
        questionnaire = self.get_object()
        to_email = request.data.get('to_email',None)
        if not to_email:
            raise exceptions.BadRequest(_("Email id required"))
        questionnaire.share(to_email)
        return response.SuccessResponse("Email send successfully")


class CreateLink(generics.RetrieveAPIView):
    """
    Returns public link for questionnaire.
    """

    def get_object(self):
        """
        Return questionnaires of current node.
        """
        try:
            questionnaire = question_models.Questionnaire.objects.get(
                id=self.kwargs['pk'], owner=session.get_current_node(),
                is_deleted=False
                )
        except:
            raise exceptions.NotFound(_(
                'Questionnaire does not exist'))
        return questionnaire

    def get(self, request, *args, **kwargs):
        """
        Creates/gets questionnaire public link.
        """
        questionnaire = self.get_object()
        response_data = {
            "link": questionnaire.create_link()
        }
        return response.SuccessResponse(response_data)


class CheckQuestionnaireAvailability(generics.CreateAPIView):
    """
    Checks the questionnaire name already exists or not.
    """

    def create(self, request, *args, **kwargs):
        """
        Create overrided to check the questionnaires with the given name.
        """
        data = {
            "is_existing": False
        }
        name = request.data.get('name',None)
        questionnaires = question_models.Questionnaire.objects.filter(
            name__iexact=name,owner=session.get_current_node(),
            is_deleted=False)
        if questionnaires.exists():
            data['is_existing'] = True
        
        return response.SuccessResponse(data)
