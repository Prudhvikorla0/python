"""Constants under the supplychain section are stored here."""

from django.db import models
from django.utils.translation import gettext_lazy as _

CONNECT_ID_FORMAT = "{r5}-{r5}-{r5}"
TRACE_CODE_FORMAT = "RO{y}-{R10}"

class NodeType(models.IntegerChoices):
    COMPANY = 101, _('Company')
    PRODUCER = 111, _('Producer')


class NodeStatus(models.IntegerChoices):
    ACTIVE = 101, _('Active')
    INACTIVE = 111, _('Inactive')


class NodeMemberType(models.IntegerChoices):
    SUPER_ADMIN = 101, _('Super Admin')
    ADMIN = 111, _('Admin')
    CONNECTION_MANAGER = 121, _('Connection Manager')
    TRANSACTION_MANAGER = 131, _('Transaction Manager')
    REPORTER = 141, _('Reporter')


class NodeDocumentType(models.IntegerChoices):
    COMPANY_DOCUMENT = 101, _('Company Document')
    INCORPORATION_DOCUMENT = 102, _('Incorporation Document')
    CERTIFICATION = 103, _('Certification')
    ANNUAL_REPORT = 104, _('Annual Report')


COMPANY_PROFILE_FIELDS = ['name', 'description', 'street', 'city', 'province',
                          'country', 'image', 'registration_no', 'phone', 'email', 
                          'contact_name', 'sub_province',]


class NodeVisibilityType(models.IntegerChoices):
    TENANT_SPECIFIC = 101, _('Tenant Specific')
    VISIBLE = 111, _('Visible')
    ANONYMOUS = 121, _('Fully Anonymous')

class DataSyncServers(models.IntegerChoices):
    RO_AI = 101, _('RO AI')
