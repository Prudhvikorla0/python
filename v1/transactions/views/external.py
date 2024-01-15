from django.db.models import Q

from rest_framework import filters
from rest_framework import generics

from base.views import IdDecodeModelViewSet
from base import session

from v1.transactions.serializers import external as ext_serializers
from v1.transactions import models as transaction_models
from v1.transactions import filters as txn_filters
from v1.transactions import constants as txn_consts


class ExternalTransactionViewSet(IdDecodeModelViewSet):
    """
    View to get, create and update external transactions.
    """

    http_method_names = ['get', 'post', 'patch',]
    filterset_class = txn_filters.ExternalTransactionFilter

    def get_queryset(self):
        """
        Return transactions related to logged-in user's node.
        """
        node = session.get_current_node()
        query = Q(source=node) | Q(destination=node)
        transactions = transaction_models.ExternalTransaction.objects.select_related(
            'source', 'destination', 'currency', 'creator', 'unit').filter(
            query).order_by('-number')
        return transactions

    def get_serializer_class(self):
        """
        Return serializer with respect request method and action.
        """
        serializer = ext_serializers.ExternalTransactionSerializer
        if self.action == 'list':
            serializer = ext_serializers.ExternalTransactionListSerializer
        return serializer


class ExternalTransactionRejectView(generics.UpdateAPIView):
    """Api to reject transaction."""

    serializer_class = ext_serializers.ExternalTransactionRejectionSerializer

    def get_queryset(self):
        """
        Return transactions where the node is destination.
        """
        node = session.get_current_node()
        exclude_statuses = [
            txn_consts.TransactionStatus.DECLINED
        ]
        if not session.get_current_tenant().transaction_auto_approval:
            exclude_statuses.append(txn_consts.TransactionStatus.APPROVED)
        transactions = transaction_models.ExternalTransaction.objects.filter(
            destination=node).exclude(status__in=exclude_statuses)
        return transactions
