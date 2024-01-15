"""Filters used in the country api."""

from django_filters import rest_framework as filters

from django.db.models import Q

from utilities.functions import decode

from base import session
from common.drf_custom import filters as custom_filters

from v1.questionnaire import models as question_models


class QuestionnaireFilter(filters.FilterSet):
    """
    Filter used in questionnaire
    """
    submitter = filters.CharFilter(
        field_name='submitter',lookup_expr='icontains')
    submitted_date = filters.DateFilter(
        field_name='submitted_date')
    tags = custom_filters.IdencodeFilter(field_name='tags')
    status = filters.NumberFilter(field_name='status')

    class Meta:
        """
        Meta Info.
        """
        model = question_models.Questionnaire
        fields = ('submitter','submitted_date','tags','status')


class QuestionFilter(filters.FilterSet):
    """
    Filter used in questions
    """
    questionnaire = custom_filters.IdencodeFilter(
        field_name='questionnaire')

    class Meta:
        """
        Meta Info.
        """
        model = question_models.Question
        fields = ('questionnaire',)
