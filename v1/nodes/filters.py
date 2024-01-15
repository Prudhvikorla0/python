"""Filters used in the country api."""

from django_filters import rest_framework as filters

from django.db.models import Q,F
from django.utils import timezone

from utilities.functions import decode

from base import session
from common.drf_custom import filters as custom_filters

from v1.nodes import constants as node_constants
from v1.nodes import models as node_models


class NodeMemberFilter(filters.FilterSet):
    """
    Filterclass for country-list api.
    """
    email = filters.CharFilter(method='email_filter')
    transacted = filters.BooleanFilter(method='transacted_filter')

    class Meta:
        """
        Meta Info.
        """
        model = node_models.NodeMember
        fields = ('email', )

    def email_filter(self, queryset, name, value):
        """
        Search filter on the basis of country name.
        """
        query = Q(user__email=value)
        return queryset.filter(query)

    def transacted_filter(self, queryset, name, value):
        current_node = session.get_current_node()
        transactors = []
        transactors += [
            i[0] for i in current_node.internaltransactions.all().values_list('creator')]
        transactors += [
            i[0] for i in current_node.outgoing_transactions.all().values_list('creator')]
        transactors += [
            i[0] for i in current_node.incoming_transactions.all().values_list('creator')]
        return queryset.filter(user__id__in=transactors)


class NodeFilter(filters.FilterSet):
    """
    Filter to filter connections
    """

    type = filters.ChoiceFilter(choices=node_constants.NodeType.choices)
    status = filters.ChoiceFilter(choices=node_constants.NodeStatus.choices)
    exclude_existing = filters.BooleanFilter(method='filter_exclude_existing')
    connection_status = filters.NumberFilter(method='filter_connection_status')
    tags = filters.CharFilter(method='filter_tags')
    connect_id = filters.CharFilter()

    class Meta:
        model = node_models.Node
        fields = ['type', 'status', 'is_producer', 'connection_status',]

    def filter_exclude_existing(self, queryset, name, value):
        """
        Exclude existing nodes from the list.
        """
        if value:
            current_sc = self.request.GET.get('supply_chain', None)
            current_sc_id = decode(current_sc) if current_sc else None
            current_node = session.get_current_node()
            connections = current_node.get_connections(
                supply_chain=current_sc_id, include_revoked=True)
            ids = connections.values_list('id', flat=True)
            queryset = queryset.exclude(id__in=ids)
        return queryset

    def filter_connection_status(self, queryset, name, value):
        """
        Filter by connection status
        """
        if value:
            current_node = session.get_current_node()
            queryset = queryset.filter(
                target_connections__source=current_node, 
                target_connections__status=value)
        return queryset
    
    def filter_tags(self, queryset, name, value):
        if value:
            queryset = queryset.filter(target_connections__tags=decode(value))
        return queryset


class FolderFilter(filters.FilterSet):
    """
    Filter for folder.
    """
    created_on = filters.DateFilter(
        field_name='created_on__date')
    
    class Meta:
        """
        Meta Info.
        """
        model = node_models.Folder
        fields = ('created_on',)


class NodeDocumentFilter(filters.FilterSet):
    """
    Filter for node document.
    """
    created_on = filters.DateFilter(
        field_name='created_on__date')
    expiry_date = filters.DateFilter(
        field_name='expiry_date')
    nearest_expiring = filters.BooleanFilter(
        method='nearest_expiring_filter')
    folder = custom_filters.IdencodeFilter(
        field_name='folder')
    
    def nearest_expiring_filter(self, queryset, name, value):
        """
        ordering the files based on expiry
        """
        if value:
            return queryset.filter(
                expiry_date__gte=timezone.now().date()).order_by(
                    'expiry_date')
        return queryset
    
    class Meta:
        """
        Meta Info.
        """
        model = node_models.NodeDocument
        fields = (
            'created_on','expiry_date','nearest_expiring',
            'folder')
