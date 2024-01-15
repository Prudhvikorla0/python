"""Constants under the supplychain section are stored here."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class ConnectionStatus(models.IntegerChoices):
    PENDING = 101, _('Pending')
    APPROVED = 111, _('Approved')
    REVOKED = 121, _('Revoked')


class ConnectionInitiation(models.IntegerChoices):
    MANUAL = 101, _('Manual')
    SYSTEM = 201, _('System')
