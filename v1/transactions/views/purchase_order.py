from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response

from base import session
from base.views import IdDecodeModelViewSet
from utilities.functions import decode
from v1.transactions import filters as txn_filters, models as transaction_models
from v1.transactions.serializers import purchase_order as purchase_order_serializers


class PurchaseOrderView(IdDecodeModelViewSet):
    """
     Viewset to create, list, update and remove purchase order.
    """
    http_method_names = ['get', 'post', 'patch', 'delete']
    filterset_class = txn_filters.PurchaseOrderFilter
    serializer_class = purchase_order_serializers.PurchaseOrderSerializer

    def get_queryset(self):
        """
        Function for filter transaction enquiry by current node.
        """
        node = session.get_current_node()
        query = Q(sender=node) | Q(receiver=node)
        purchase_order = transaction_models.PurchaseOrder.objects.select_related(
            'sender', 'receiver', 'creator', 'updater', 'product',
            'currency', 'unit', 'submission_form').prefetch_related('claims').filter(
            query).distinct('number').order_by('-number')
        return purchase_order


class DeliveryNotificationView(IdDecodeModelViewSet):
    """
     Viewset to create, list delivery notifications.
    """
    http_method_names = ['get', 'post', 'patch']
    serializer_class = purchase_order_serializers.DeliveryNotificationSerializer
    queryset = transaction_models.DeliveryNotification.objects.all(
        ).order_by('-expected_date')

    @action(methods=['post'], detail=False)
    def purchase(self, request, **kwargs):
        """ Function for list delivery notification based on purchase order."""
        data = []
        for delivery_noti in \
                transaction_models.DeliveryNotification.objects.filter(
                purchase_order__id=decode(request.data['purchase_order'])):
            data.append(purchase_order_serializers.BasicDeliveryNotificationSerializer(
                delivery_noti).data)
        response = {
            'count': len(data),
            'results': data}
        return Response(response)
