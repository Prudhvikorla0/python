"""Filters used in the country api."""

from cgitb import lookup
from codecs import lookup_error
from random import choices
from django_filters import rest_framework as filters

from django.db.models import Q
from base import session
from utilities.functions import decode

from common.library import _unix_to_datetime
from common.drf_custom import filters as custom_filters

from v1.transactions import models as trans_models
from v1.transactions import constants as txn_consts


class ExternalTransactionFilter(filters.FilterSet):
    """
    Filterclass for external transaction.
    """

    product = filters.CharFilter(method='product_filter')
    supply_chain = filters.CharFilter(method='supplychain_filter')
    type = filters.NumberFilter(method='type_filter')
    purchase_order = filters.CharFilter(method='po_filter')
    node = filters.CharFilter(method='node_filter')
    search = filters.CharFilter(method='search_filter')
    creator = custom_filters.IdencodeFilter()

    class Meta:
        """
        Meta Info.
        """
        model = trans_models.ExternalTransaction
        fields = ('product', 'type', 'status', 'supply_chain', 'search', 'creator')

    def search_filter(self, queryset, name, value):
        query = Q(source__name__icontains=value) | \
                Q(destination__name__icontains=value) | Q(
                    number__icontains=value) | Q(
                    source_batches__product__name__icontains=value) | Q(
                        result_batches__product__name__icontains=value)
        return queryset.filter(query).distinct()

    def product_filter(self, queryset, name, value):
        """
        """
        product_id = decode(value)
        query = Q(source_batches__product__id=product_id) | \
                Q(result_batches__product__id=product_id)
        return queryset.filter(query).distinct()

    def supplychain_filter(self, queryset, name, value):
        """
        """
        supplychain_id = decode(value)
        query = Q(source_batches__product__supply_chain__id=supplychain_id) | \
                Q(result_batches__product__supply_chain__id=supplychain_id)
        return queryset.filter(query).distinct()

    def type_filter(self, queryset, name, value):
        current_node = session.get_current_node()
        if value == txn_consts.ExternalTransactionType.REVERSAL:
            queryset = queryset.filter(type=value)
        elif value == txn_consts.ExternalTransactionType.INCOMING:
            queryset = queryset.filter(
                destination=current_node).exclude(
                type=txn_consts.ExternalTransactionType.REVERSAL)
        else:
            queryset = queryset.filter(
                source=current_node).exclude(
                type=txn_consts.ExternalTransactionType.REVERSAL)
        return queryset

    def po_filter(self, queryset, name, value):
        """
        """
        po_id = decode(value)
        query = Q(purchase_order__id=po_id)
        return queryset.filter(query)

    def node_filter(self, queryset, name, value):
        node_id = decode(value)
        query = Q(source__id=node_id) | Q(destination__id=node_id)
        return queryset.filter(query).distinct()


class InternalTransactionFilter(filters.FilterSet):
    """
    Filterclass for internal transaction.
    """

    product = filters.CharFilter(method='product_filter')
    supply_chain = filters.CharFilter(method='supplychain_filter')
    search = filters.CharFilter(method='search_filter')
    creator = custom_filters.IdencodeFilter()

    class Meta:
        """
        Meta Info.
        """
        model = trans_models.InternalTransaction
        fields = ('product', 'type', 'supply_chain', 'search', 'creator')

    def product_filter(self, queryset, name, value):
        """
        """
        product_id = decode(value)
        query = Q(source_batches__product__id=product_id) | \
                Q(result_batches__product__id=product_id)
        return queryset.filter(query).distinct()

    def supplychain_filter(self, queryset, name, value):
        """
        """
        supplychain_id = decode(value)
        query = Q(source_batches__product__supply_chain__id=supplychain_id) | \
                Q(result_batches__product__supply_chain__id=supplychain_id)
        return queryset.filter(query).distinct()

    def search_filter(self, queryset, name, value):
        query = Q(source_batches__product__name__icontains=value) | \
                Q(result_batches__product__name__icontains=value) | Q(
                    number__icontains=value)
        return queryset.filter(query).distinct()


class PurchaseOrderFilter(filters.FilterSet):
    """
    Filter class for Purchase Order.
    """

    product = filters.CharFilter(method='product_filter')
    date_after = filters.DateFilter(field_name='expected_date', lookup_expr='gte')
    date_before = filters.DateFilter(field_name='expected_date', lookup_expr='lte')
    search = filters.CharFilter(method='search_fields')
    type = filters.NumberFilter(method='filter_type')
    supply_chain = filters.CharFilter(method='supply_chain_filter')
    status = filters.CharFilter(method='status_filter')

    class Meta:
        """
        Meta Info.
        """
        model = trans_models.PurchaseOrder
        fields = ('product', 'date_after', 'date_before', 'status', 'search', 'type')

    def product_filter(self, queryset, name, value):
        product_id = decode(value)
        query = Q(product__id=product_id)
        return queryset.filter(query)

    def search_fields(self, queryset, name, value):
        query = Q()
        query |= Q(number__icontains=value)
        query |= Q(receiver__name__icontains=value)
        return queryset.filter(query)

    def filter_type(self, queryset, name, value):
        """Filter purchase order by type with received or send"""
        current_node = session.get_current_node()
        query = Q()
        if value == txn_consts.PurchaseOrderType.RECEIVED_ORDER:
            query |= Q(receiver=current_node)
        elif value == txn_consts.PurchaseOrderType.SEND_ORDER:
            query |= Q(sender=current_node)
        return queryset.filter(query)

    def supply_chain_filter(self, queryset, name, value):
        sc_id = decode(value)
        query = Q(product__supply_chain__id=sc_id)
        return queryset.filter(query)

    def status_filter(self, queryset, name, value):
        if value:
            values = [int(status) for status in value.split(',') if status]
            query = Q(status__in=values)
        return queryset.filter(query)
