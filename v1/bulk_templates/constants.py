"""Constants under the user accounts section are stored here."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from base.choices import CallableIntegerChoices

from . import data_generators
from . import validators
from . import template_config


class TemplateType(CallableIntegerChoices):
    TRANSACTION = 101, template_config.TransactionTemplate, _('Transaction')
    CONNECTION = 111, template_config.ConnectionTemplate, _('Connection')
    QUESTIONNAIRE = 121, template_config.QuestionnaireTemplate, _('Questionnaire')


class TemplateFieldTypes(CallableIntegerChoices):
    PRIMARY_KEY = 51, validators.pk_validator, _('Primary Key')
    STRING = 101, validators.string_validator, _('String')
    INTEGER = 111, validators.integer_validator, _('Integer')
    POSITIVE_INTEGER = 115, validators.positive_integer_validator, _('Positive Integer')
    FLOAT = 121, validators.float_validator, _('Float')
    POSITIVE_FLOAT = 125, validators.positive_float_validator, _('Positive Float')
    DATE = 131, validators.date_validator, _('Date')
    PHONE = 141, validators.phone_validator, _('Phone')
    EMAIL = 151, validators.email_validator, _('Email')
    BOOL = 161, validators.bool_validator, _('Boolean')


class DataGenerator(CallableIntegerChoices):
    COUNTRIES = 101, data_generators.get_countries, _('Countries')
    PROVINCES = 201, data_generators.get_provinces, _('Provinces')
    PRODUCERS = 301, data_generators.get_producers, _('Producers')
    PRODUCTS = 401, data_generators.get_products, _('Products')
    OPERATIONS = 501, data_generators.get_operations, _('Operations')
    CURRENCIES = 601, data_generators.get_currencies, _('Currencies')
    UNITS = 701, data_generators.get_units, _('Units')


class BulkUploadStatuses(models.IntegerChoices):
    CREATED = 101, _('Created')
    VALIDATED = 201, _('Validated')
    INITIATED = 301, _('Initiated')
    IN_PROGRESS = 401, _('In Progress')
    COMPLETED = 501, _('Completed')
    FAILED = 601, _('Failed')
