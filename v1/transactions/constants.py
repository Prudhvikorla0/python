"""Constants under the tenant section are stored here."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class TransactionType(models.IntegerChoices):

    EXTERNAL = 101, _('External Transaction')
    INTERNAL = 111, _('Internal Transaction')


class TransactionStatus(models.IntegerChoices):
    CREATED = 101, _('Transaction Created')
    DECLINED = 111, _('Transaction Declined')
    ON_HOLD = 121, _('Transaction On-hold')
    APPROVED = 131, _('Transaction  Approved')


class InternalTransactionType(models.IntegerChoices):
    PROCESSING = 101, _('Processing')
    LOSS = 111, _('Loss')
    MERGE = 121, _('Merge')


class TransactionMode(models.IntegerChoices):
    MANUAL = 101, _('Manual')
    SYSTEM = 111, _('System')


class ExternalTransactionType(models.IntegerChoices):
    INCOMING = 101, _('Incoming')
    OUTGOING = 111, _('Outgoing')
    REVERSAL = 121, _("Reversal")
    INCOMING_WITHOUT_SOURCE = 131, _('Incoming Without Source')


class PurchaseOrderStatus(models.IntegerChoices):
    PENDING = 101, _('Pending')
    APPROVED = 111, _('Approved')
    REJECTED = 121, _('Rejected')
    ON_HOLD = 131, _('On-hold')
    CANCELLED = 141, _('Cancelled')
    PARTIAL = 151, _('Partial')


class TransactionEnquiryType(models.IntegerChoices):
    PURCHASE_ORDER = 101, _('Purchase Order')
    SENDER_ENQUIRY = 111, _('Sender Enquiry')


class PurchaseOrderType(models.IntegerChoices):
    RECEIVED_ORDER = 101
    SEND_ORDER = 201


class TransactionRejectionReason(models.IntegerChoices):
    QUALITY_ISSUE = 101, _('Quality Issue')
    DATA_ISSUE = 111, _('Data Issue')
    OTHER = 121, _("Other Reason")


# txn type colours used in tracker

external_transaction_colours = {
    ExternalTransactionType.INCOMING : {
        "primary": "#D8C304", 
        "secondary": "#d8c30433"
    }, 
    ExternalTransactionType.INCOMING_WITHOUT_SOURCE : {
        "primary": "#D8C304", 
        "secondary": "#d8c30433"
    }, 
    ExternalTransactionType.OUTGOING: {
        "primary": "#219653", 
        "secondary": "#EEF3E9"
    }
}

internal_transaction_colours = {
    InternalTransactionType.MERGE : {
        "primary": "#ED7F2F", 
        "secondary": "#ed7f2f33"
    }, 
    InternalTransactionType.PROCESSING : {
        "primary": "#2F80ED", 
        "secondary": "#2f80ed33"
    }
}

origin_transaction_colours = {
        "primary": "#3B04D8", 
        "secondary": "#3b04d833"
}
