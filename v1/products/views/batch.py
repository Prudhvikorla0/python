from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from base.views import IdDecodeModelViewSet
from base import session

from v1.products.serializers import batch as batch_serializers
from v1.products import models as product_models
from v1.products import filters as produt_filters

from v1.transactions import constants as txn_consts


class BatchViewSet(IdDecodeModelViewSet):
    """
    View to list and retrieve batch data.
    """

    http_method_names = ['get', 'post', 'patch',]
    serializer_class = batch_serializers.BatchListSerializer
    filter_class = produt_filters.BatchFilter

    def get_queryset(self):
        """
        Return batches of logged-in users current node.
        """
        node = session.get_current_node()
        if self.request.query_params.get('select_all', False):
            self.pagination_class = None
        batches = (product_models.Batch.objects.filter(
            node=node, 
            incoming_transactions__status=txn_consts.TransactionStatus.APPROVED
        ) | product_models.Batch.objects.filter(
            node=node, 
            incoming_transactions=None
        )).distinct().select_related('product', 'unit').prefetch_related(
            'batch_claims').order_by('-number')
        if not session.get_current_tenant().show_empty_batches:
            batches = batches.filter(current_quantity__gt=0.0)
        return batches

    def get_serializer_class(self):
        """
        Change serializer with respect to action.
        """
        serializer = batch_serializers.BatchSerializer
        if self.action == 'list':
            serializer = batch_serializers.BatchListSerializer
        elif self.action == 'create':
            serializer = batch_serializers.CreateBatchSerializer

        return serializer
