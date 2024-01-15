from django.contrib import admin

from common.admin import BaseAdmin

from v1.transactions import models as tnx_models


class TransactionAdmin(BaseAdmin):
    """ Admin for Base transaction """
    list_display = ('idencode', 'status', 'transaction_type')
    readonly_fields = BaseAdmin.readonly_fields + ('parents', 'source_batches',)
    list_filter = ('transaction_type', 'status', 'tenant')


class ExternalTransactionAdmin(TransactionAdmin):
    """ Admin for External transaction"""
    list_display = (
        'idencode', 'source', 'destination', 'status', 'type')
    search_fields = [
                     'source__name',
                     'destination__name',
                     ]
    ordering = ('-id',)
    list_filter = ('transaction_type', 'status', 'type')


class InternalTransactionAdmin(TransactionAdmin):
    """ Admin for Internal transactions """
    list_display = ('idencode', 'node', 'type', 'mode')
    search_fields = ['node__name',]
    list_filter = ('transaction_type', 'status', 'type', 'mode')


class SourceBatchAdmin(BaseAdmin):
    """ Admin for Internal transactions """
    list_display = ('idencode', 'transaction', 'batch')


class PurchaseOrderAdmin(BaseAdmin):
    """ Admin for Purchase order """
    list_display = ('idencode', 'sender', 'receiver')
    search_fields = ['sender__name', 'receiver__name']
    list_filter = ('status',)


class DeliveryNotificationAdmin(BaseAdmin):
    """ Admin for delivery notification """
    list_display = ('idencode', 'purchase_order', 'expected_date')
    search_fields = ['purchase_order__sender__name',
                     'purchase_order__receiver__name']


admin.site.register(tnx_models.Transaction, TransactionAdmin)
admin.site.register(tnx_models.SourceBatch, SourceBatchAdmin)
admin.site.register(tnx_models.InternalTransaction, InternalTransactionAdmin)
admin.site.register(tnx_models.ExternalTransaction, ExternalTransactionAdmin)
admin.site.register(tnx_models.PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(tnx_models.DeliveryNotification, DeliveryNotificationAdmin)
admin.site.register(tnx_models.TransactionComment)
