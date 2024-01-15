"""URLs of the app supply-chains."""

from rest_framework import routers
from django.urls import path

from v1.supply_chains.views import supply_chain as supply_viewset
from v1.supply_chains.views import connection as conn_views
from v1.supply_chains import models as supply_models


router = routers.SimpleRouter()

router.register(
    r'node/operations', supply_viewset.OperationViewSet,
    basename=supply_models.Operation)

urlpatterns = router.urls

urlpatterns += [
    path('', supply_viewset.SupplyChainView.as_view(),
         name='supplychain-list-create'),
    path('connection/', conn_views.ConnectionsView.as_view(),
         name='connection-add'),
    path('connection/<idencode:pk>/', conn_views.ConnectionDetails.as_view(),
         name='connection-details'),
]
