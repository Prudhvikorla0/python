"""
APIs for Connections
"""

from rest_framework import views
from rest_framework import generics
from rest_framework import filters
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, Window
from django.db.models.functions import Rank

from django.db.models import Q, F

from base import session
from base import views as custom_views
from base import exceptions

from utilities.functions import decode

from v1.nodes import models as node_models
from v1.nodes import filters as node_filters

from v1.supply_chains import filters as sc_filters
from v1.supply_chains.serializers import connections as conn_serializers
from v1.supply_chains import models as sc_models
from v1.nodes.serializers import node as node_serializers

# Create your views here.


class ConnectionsView(generics.ListCreateAPIView):
    """
    API to add and list connections
    """
    # http_method_names = ['post', 'get']
    filterset_class = sc_filters.ConnectionFilter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'type', 'email', 'contact_name', 'number']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return conn_serializers.ConnectNodeSerializer
        return node_serializers.NodeConnectionSerializer

    def get_queryset(self):
        """
        Get connection for currently active node.
        """
        current_node = session.get_current_node()
        buyers = self.request.GET.get('buyers', True)
        suppliers = self.request.GET.get('suppliers', True)
        include_revoked = self.request.GET.get('include_revoked', False)
        assert buyers or suppliers, "Either buyers or suppliers should be True"

        params = {
            'buyers': buyers,
            'suppliers': suppliers,
            'include_revoked': include_revoked,
        }
        if 'supply_chain' in self.request.GET and not self.request.GET.get(
                'exclude_existing', False):
            current_sc = decode(self.request.GET.get('supply_chain', None))
            params['supply_chain'] = current_sc
        connected_nodes = current_node.get_connections(**params)
        connected_nodes = connected_nodes.annotate(
            rank=Window(
                expression=Rank(),
                order_by = F('risk_scores__overall').desc(nulls_last=True),
            )
        )
        return connected_nodes


class ConnectionDetails(generics.RetrieveUpdateAPIView):
    """
    API to get the details of a connection.
    """

    serializer_class = conn_serializers.ConnectionSerializer

    def get_queryset(self):
        current_node = session.get_current_node()
        queryset = current_node.source_connections.all()
        return queryset
