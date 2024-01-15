from django.db import models
from django.utils.translation import gettext_lazy as _

import datetime

from base.models import AbstractBaseModel
from base import session

from v1.questionnaire import constants as question_consts
from v1.questionnaire import notifications

from v1.nodes import constants as node_consts

from v1.accounts.models import ValidationToken
from v1.accounts import constants as user_consts

from . import tasks



class Questionnaire(AbstractBaseModel):
    """
    Model to save questionnaire related information.
    """
    owner = models.ForeignKey(
        'nodes.Node', on_delete=models.CASCADE,
        default=None, related_name='questionnaires', 
        verbose_name=_('Questionnaire Owner'))
    tags = models.ManyToManyField(
        'tenants.Tag', related_name='questionnaires',
        verbose_name=_('Questionnaire Tags'))
    
    name = models.CharField(
        default='', null=True, blank=True, max_length=500, 
        verbose_name=_('Questionnaire Name'))
    description = models.TextField(
        default='', null=True, blank=True,
        verbose_name=_('Questionnaire Description'))
    submitter = models.CharField(
        default='', null=True, blank=True, max_length=500, 
        verbose_name=_('Questionnaire Submitted By'))
    submitted_date = models.DateField(
        default=datetime.date.today, verbose_name=_('Submitted Date'))
    status = models.IntegerField(
        default=question_consts.QuestionnaireStatus.GENERATING_ANSWER,
        choices=question_consts.QuestionnaireStatus.choices, 
        verbose_name=_('Status Of Questionnaire'))
    is_deleted = models.BooleanField(
        default=False, verbose_name='Is Deleted')
    
    def __str__(self) -> str:
        return f'{self.name} - {self.owner} - {self.idencode}'
    
    @property
    def total_questions(self):
        """
        Return total number of questions.
        """
        return self.questions.filter(is_deleted=False).count()
    
    def share(self,send_to):
        """
        Method used to share questionnaire to given email.
        """
        token = None
        user = session.get_current_user()
        token = ValidationToken.initialize(
            user,user_consts.ValidationTokenType.QUESTIONNAIRE_SHARE)
        notification_manager = notifications.ShareQuestionnaireNotificationManager(
            user=user, action_object=self, token=token,send_to=send_to)
        notification_manager.send_notification()

    def create_link(self):
        """
        Method to create share link for questionnaire.
        """
        user = session.get_current_user()
        tenant = session.get_current_tenant()
        token = ValidationToken.initialize(
            user,user_consts.ValidationTokenType.QUESTIONNAIRE_LINK)
        url = tenant.get_base_url() /'public/questionnaire'
        params = f'token={token.key}&salt={token.idencode}&questionnaire={self.idencode}'
        link = f'{url}{params}'
        return link
    
    def all_questions_answered(self):
        """
        Checks all the questions of the questionnaire is 
        answered.
        """
        questions = self.questions.filter(is_deleted=False)
        answers = Answer.objects.filter(
            question__in=questions,is_deleted=False).order_by(
                'question__id').distinct('question__id')
        if questions.count() <= answers.count():
            return True
        return False
    
    def answer_generation_complete(self):
        """
        Set the questionnaire status into approval waiting.
        """
        self.status = question_consts.QuestionnaireStatus.APPROVAL_WAITING
        self.save()
        return True
    
    def approve(self):
        """
        Set the questionnaire status into approval waiting.
        """
        self.status = question_consts.QuestionnaireStatus.APPROVED
        self.save()
        return True

    
class Question(AbstractBaseModel):
    """
    Model to save questions under the questionnaire.
    """
    questionnaire = models.ForeignKey(
        Questionnaire, on_delete=models.CASCADE,
        default=None, related_name='questions', 
        verbose_name=_('Questionnaire'))
    question = models.TextField(
        default='', null=True, blank=True,
        verbose_name=_('Question'))
    synced_to = models.IntegerField(
        default=None,
        choices=node_consts.DataSyncServers.choices,
        verbose_name=_('Question Synced To'),null=True,blank=True)
    is_deleted = models.BooleanField(
        default=False, verbose_name='Is Deleted')
    
    def __str__(self) -> str:
        return f'{self.question} - {self.questionnaire} - {self.idencode}'
    
    class Meta:
        """ordering added."""
        ordering = ['id']

    def save(self, *args, **kwargs):
        """
        Override to fetch answer from LLM
        """
        new = not bool(self.id)
        super(AbstractBaseModel, self).save(*args, **kwargs)
        if new:
            self.answer_question()

    def answer_question(self):
        """
        Function to get answer from LLM
        """
        tasks.find_answer.delay(question_id=self.id)
        return True

    @property
    def is_answered(self):
        """
        Return is the question answered or not. 
        """
        return self.answers.exists()
    
    @property
    def answer_generating(self):
        """Is answer is generating for this question."""
        return (not self.answers.exists()) and (
            self.questionnaire.status == question_consts.QuestionnaireStatus.GENERATING_ANSWER)
    
    @property
    def answer(self):
        """
        Return latest answer of the question.
        """
        return self.answers.latest('id')
    

class Answer(AbstractBaseModel):
    """
    Model to save answers of a question.
    """
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        default=None, related_name='answers', 
        verbose_name=_('Question'))
    files = models.ManyToManyField(
        'nodes.NodeDocument', related_name='created_answers',
        verbose_name=_('Referred Documents'))

    answer = models.TextField(
        default='', null=True, blank=True,
        verbose_name=_('Answer'))
    synced_to = models.IntegerField(
        default=None,
        choices=node_consts.DataSyncServers.choices,
        verbose_name=_('Answer Synced To'),null=True,blank=True)
    type = models.IntegerField(
        default=question_consts.AnswerType.AUTOMATIC,
        choices=question_consts.AnswerType.choices,
        verbose_name=_('Answer Synced To'),null=True,blank=True)
    is_deleted = models.BooleanField(
        default=False, verbose_name='Is Deleted')
    
    def __str__(self) -> str:
        return f'{self.question} - {self.answer}'
