"""Constants under the supplychain section are stored here."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Severity(models.IntegerChoices):
    LOW = 101, _('Low')
    MEDIUM = 201, _('Medium')
    HIGH = 301, _('High')


class Category(models.IntegerChoices):
    ENVIRONMENT = 101, _('Environment')
    SOCIAL = 201, _('Social')
    GOVERNANCE = 301, _('Governance')
    OVERALL = 1001, _('Overall')


class RiskLevel(models.IntegerChoices):
    RISKY = 101, _('Risky')
    SAFE = 201, _('Safe')
    ALL = 1001, _('All')
