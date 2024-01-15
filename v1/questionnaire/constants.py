"""Constants under the tenant section are stored here."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class QuestionnaireStatus(models.IntegerChoices):

    GENERATING_ANSWER = 101, _('Generating Answers')
    APPROVAL_WAITING = 111, _('Waiting For Approval')
    APPROVED = 121, _('Approved')


class AnswerType(models.IntegerChoices):

    AUTOMATIC = 101, _('Automatically Created')
    MANUAL = 111, _('Manually Created')
    BOTH = 121, _('Automatic, Manually Updated')
