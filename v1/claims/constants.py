"""Constants under the user claims section are stored here."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from v1.transactions.constants import ExternalTransactionType, InternalTransactionType


class ClaimType(models.IntegerChoices):
    PRODUCT_CLAIM = 101, _('Product Claim')
    COMPANY_CLAIM = 111, _('Company Claim')
    CONNECTION_CLAIM = 121, _('Connection Claim')


class ClaimGroup(models.IntegerChoices):
    CERTIFICATION = 101, _('Certification Claim')
    DOCUMENT = 111, _('Document Claim')
    SELF_ASSESSMENT = 121, _('Self Assessment')


class ClaimInheritanceType(models.IntegerChoices):
    NEVER = 101, _('Never Inherit')
    ALWAYS = 111, _('Always Inherit')
    PRODUCT = 121, _('Product Inheritance')


class ClaimVerificationMethod(models.IntegerChoices):
    NONE = 101, _('None')
    SYSTEM = 111, _('System')
    SECOND_PARTY = 121, _('Second Party')
    THIRD_PARTY = 131, _('Third Party')


class ClaimVerificationType(models.IntegerChoices):
    SYSTEM = 101, _('System')
    MANUAL = 111, _('Second Party')


class ClaimStatus(models.IntegerChoices):
    PENDING = 101, _('Pending')
    APPROVED = 111, _('Approved')
    REJECTED = 121, _('Rejected')
    PARTIAL = 131, _('Partial')
    ON_HOLD = 141, _('On Hold')
    EXPIRED = 151, _('Expired')


class ClaimAttachedVia(models.IntegerChoices):
    MANUAL = 101, _('Manual')
    INHERITANCE = 111, _("Inheritance")
    SYNC = 121, _('Sync')


class ClaimAttachedTo(models.IntegerChoices):
    BATCH = 101, _('Batch')
    NODE = 111, _('Node')
    CONNECTION = 121, _('Connection')

class ClaimAddedBy(models.IntegerChoices):
    TENANT = 101, _('Tenant')
    RO_AI = 111, _('RO_AI')

class ClaimTransactionType(models.IntegerChoices):
    INCOMING_AND_PROCESSING = 101, _('Processing And Incoming')
    OUTGOING_AND_LOSS = 111, _('Outgoing And Loss')
    MERGE_AND_REVERSAL = 121, _('Merge And Reversal')
    INCOMING_WITHOUT_SOURCE = 131, _('Incoming Without Source')
