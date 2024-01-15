"""Constants under the tenant section are stored here."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class TenantAdminType(models.IntegerChoices):
    ADMIN = 101, _('Admin')
    SUPER_ADMIN = 201, _('Super Admin')


class NodeAnonymityType(models.IntegerChoices):
    FULLY_VISIBLE = 101, _('Fully Visible')
    FULLY_ANONYMOUS = 111, _('Fully Anonymous')
    NODE_MANAGED_VISIBLE_DEFAULT = 121, _('Node Managed Visible Default')
    NODE_MANAGED_ANONYMOUS_DEFAULT = 131, _('Node Managed Anonymous Default')

class DiscoverabilityType(models.IntegerChoices):
    ALWAYS = 101, _('Always')
    NODE_PREFERENCE = 201, _('Node Preference')
    HIDDEN = 301, _('Hidden (Still will be able to connect with Connect-ID)')

class CIAvailability(models.IntegerChoices):

    NOT_AVAILABLE = 101, _('CI Not Available')
    TENANT_LEVEL = 111, _('Tenant Level')
    NODE_LEVEL = 121, _('Node Level')


class CategoryType(models.IntegerChoices):

    NODE_DOCUMENT = 101, _('Node Document')


class NodeDataTransparency(models.IntegerChoices):
    FULLY_TRANSPARENT = 101, _('Fully Transparent')
    PARTIALY_TRANSPARENT = 111, _('Partialy Transparent')
