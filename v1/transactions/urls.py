"""URLs of the app transactions."""
from django.urls import path

from rest_framework import routers

from v1.transactions.views import external as ext_txn_viewset
from v1.transactions.views import internal as int_txn_viewset
from v1.transactions.views import transaction as txn_viewset
from v1.transactions.views import purchase_order as po_viewset

from v1.transactions import models as txn_models


router = routers.SimpleRouter()

router.register(r'external', ext_txn_viewset.ExternalTransactionViewSet, 
    basename=txn_models.ExternalTransaction)
router.register(r'internal', int_txn_viewset.InternalTransactionViewSet, 
    basename=txn_models.InternalTransaction)
router.register(
    r'purchase-order', po_viewset.PurchaseOrderView,
    basename=txn_models.PurchaseOrder)
router.register(
    r'delivery-notification', po_viewset.DeliveryNotificationView,
    basename=txn_models.DeliveryNotification)

urlpatterns = router.urls

urlpatterns += [
    path('validate/', txn_viewset.ValidateTransaction.as_view(), 
    name='validate-transaction'),
    path('external/<idencode:pk>:reject', 
    ext_txn_viewset.ExternalTransactionRejectView.as_view(), 
    name='external-transaction-reject'), 
    path('<idencode:id>/comment/', 
        txn_viewset.TransactionCommentCreateListView.as_view(), 
        name='txn-comment-list-create'), 
    path('comment/<idencode:pk>/', 
        txn_viewset.TransactionCommentRetrieveView.as_view(), 
        name='txn-comment-retrieve-delete'), 
    path('<idencode:pk>/batches/', txn_viewset.TransactionBatchView.as_view(), 
         name='txn-batches'),
]
