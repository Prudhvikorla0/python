from rest_framework import filters

from base.views import IdDecodeModelViewSet
from base import session

from v1.transactions.serializers import internal as int_serializers
from v1.transactions import models as transaction_models
from v1.transactions import filters as txn_filters


class InternalTransactionViewSet(IdDecodeModelViewSet):
    """
    View to list , create and retrieve internal transactions.
    """

    http_method_names = ['get', 'post',]
    filterset_class = txn_filters.InternalTransactionFilter

    def get_queryset(self):
        """Return internal transactions of the current-user's node."""
        transactions = transaction_models.InternalTransaction.objects.prefetch_related(
            'source_batch_objects', 'result_batches').select_related('unit').filter(
            node=session.get_current_node()).order_by('-number')
        return transactions

    def get_serializer_class(self):
        """
        Change serializer with respect to action.
        """
        serializer = int_serializers.InternalTransactionSerializer
        if self.action == 'list':
            serializer = int_serializers.InternalTransactionListSerializer
        return serializer
