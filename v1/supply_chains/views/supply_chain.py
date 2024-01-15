from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend

from base.views import IdDecodeModelViewSet
from base import session

from v1.supply_chains import models as supply_models
from v1.supply_chains.serializers import supply_chain as supply_serializers

# from v1.apiauth import permissions as auth_permissions


class OperationViewSet(IdDecodeModelViewSet):
    """
   
    """

    serializer_class = supply_serializers.OperationSerializer
    http_method_names = ['get', 'post', 'patch',]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['node_type',]
    search_fields = ['name']

    def get_queryset(self):
        """
        """
        tenant = session.get_current_tenant()
        operations = supply_models.Operation.objects.filter(
            tenant=tenant).select_related('tenant')
        return operations


class SupplyChainView(generics.ListCreateAPIView):
    """
    """

    serializer_class = supply_serializers.SupplyChainSerializer


    def get_queryset(self):
        """
        """
        tenant = session.get_current_tenant()
        node = session.get_current_node()
        supply_chains = supply_models.SupplyChain.objects.filter(
            tenant=tenant)
        if node:
            supply_chains = supply_chains.filter(
                node_supplychains__node=node, is_active=True)
        return supply_chains
