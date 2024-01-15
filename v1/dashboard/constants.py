from django.db import models
from django.utils.translation import gettext_lazy as _


class Duration(models.IntegerField):
    """
    """
    YEARLY = 101, _('Yearly')
    MONTHLY = 111, _('Monthly')
    WEEKLY = 121, _('Weekly')
    DAILY = 131, _('Daily')
