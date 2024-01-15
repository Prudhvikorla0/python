"""Filters used in the app supply_chains."""

from django_filters import rest_framework as filters

from django.db.models import Q

from common import library as comm_lib
from common.drf_custom import filters as custom_filters

from base import session

from v1.nodes import constants as node_constants
from v1.nodes import models as node_models
from v1.supply_chains import models as supply_models

from v1.nodes import filters as node_filters


# class OperationFilter(filters.FilterSet):
#     """
#     Filter to filter connections
#     """
#
#     node_type = filters.ChoiceFilter(
#         choices=node_constants.NodeType.choices)
#
#     class Meta:
#         model = supply_models.Operation
#         fields = ['node_type',]


class ConnectionFilter(node_filters.NodeFilter):
    """
    Filter to filter connections based on NodeFilter
    """
    connection_status = filters.NumberFilter()
    is_buyer = filters.BooleanFilter(method='is_buyer_filter')
    is_supplier = filters.BooleanFilter(method='is_supplier_filter')

    def is_buyer_filter(self, queryset, name, value):
        """
        Return buyer connections of a node.
        """
        if value:
            current_node = session.get_current_node()
            query = Q(
                target_connections__source=current_node,is_buyer=value) 
            # | Q(
            #     incoming_transactions__source=current_node)
            return queryset.filter(query).distinct()
        return queryset
    
    def is_supplier_filter(self, queryset, name, value):
        """
        Return supplier connections of a node.
        """
        if value:
            current_node = session.get_current_node()
            query = Q(
                target_connections__source=current_node,is_supplier=value) 
            # | Q(
            #     outgoing_transactions__destination=current_node)
            return queryset.filter(query).distinct()
        return queryset
