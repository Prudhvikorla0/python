"""Constants under the dynamic form and field section are stored here."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class FormType(models.IntegerChoices):
    NODE_FORM = 101, _('Node Form')
    NODE_MEMBER_FORM = 111, _('Node Member Form')
    INTERNAL_TRANSACTION_FORM = 121, _('Internal Transaction Form')
    EXTERNAL_TRANSACTION_FORM = 122, _('External Transaction Form')
    CLAIM_FORM = 131, _('Claim Form')
    CONNECTION_FORM = 141, _('Connection Form')
    TRANSACTION_ENQUIRY_FORM = 151, _('Transaction Enquiry Form')
    VERIFIER_FORM = 161, _('Verifier Form')
    INTERNAL_FORM = 171, _('Internal Form')


class FieldType(models.IntegerChoices):
    TEXT = 101, _('Text')
    NUMBER = 111, _('Number')
    MAIL = 121, _('Email')
    CHECKBOX = 131, _('Check-Box')
    PARAGRAPH = 141, _('Paragraph')
    FILE = 151, _('File')
    DATE = 161, _('Date')
    DROPDOWN = 171, _('Drop Down')
    MULTI_SELECT_DROPDOWN = 172, _('MultiSelect Drop Down')
    RADIO_BUTTON = 181, _('Radio Button')


class FieldWidth(models.IntegerChoices):
    SMALL = 101, _('Small')
    MEDIUM = 111, _('Medium')
    LARGE = 121, _('Large')

SMALL_FIELDS = []
MEDIUM_FIELDS = []
LARGE_FIELDS = [FieldType.FILE]

# Mongodb model names

FORM_SUBMISSION_MONGO = 'form_submission'
mongo_db_models = []
