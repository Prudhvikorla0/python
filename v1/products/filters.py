"""Filters used in the country api."""

from django_filters import rest_framework as filters

# from rest_framework import filters
import django_filters

from django.db.models import Q

from utilities.functions import decode
from common.drf_custom import filters as custom_filters

from v1.products import models as product_models


class ProductFilter(django_filters.FilterSet):
    """
    Filterclass for country-list api.
    """
    search = filters.CharFilter(method='search_filter')
    supply_chain = filters.CharFilter(method='supply_chain_filter')

    class Meta:
        """
        Meta Info.
        """
        model = product_models.Product
        fields = ('search', 'supply_chain', 'is_raw', 'is_processed',)

    def search_filter(self, queryset, name, value):
        """
        Search filter on the basis of country name.
        """
        query = Q(name__icontains=value)
        return queryset.filter(query)

    def supply_chain_filter(self, queryset, name, value):
        """
        Search filter on the basis of country name.
        """
        query = Q(supply_chain__id=decode(value))
        return queryset.filter(query)


class BatchFilter(filters.FilterSet):
    """
    Filterclass for country-list api.
    """
    search = filters.CharFilter(method='search_filter')
    product = custom_filters.IdencodeFilter(field_name='product')
    claim = custom_filters.IdencodeFilter(
        field_name='batch_claims__claim')
    supply_chain = filters.CharFilter(method='supply_chain_filter')
    empty_stocks = filters.BooleanFilter(method='empty_stocks_filter')
    available_stocks = filters.BooleanFilter(method='available_stocks_filter')

    class Meta:
        """
        Meta Info.
        """
        model = product_models.Batch
        fields = ('search', 'product', 'claim')

    def search_filter(self, queryset, name, value):
        """
        Search filter on the basis of country name.
        """
        query = Q(product__name__icontains=value) | Q(
            name__icontains=value) | Q(number__icontains=value)
        return queryset.filter(query).distinct()

    def supply_chain_filter(self, queryset, name, value):
        """
        Search filter on the basis of country name.
        """
        query = Q(product__supply_chain__id=decode(value))
        return queryset.filter(query)
    
    def empty_stocks_filter(self, queryset, name, value):
        """
        Filter to show only empty stocks.
        """
        if value:
            query = Q(current_quantity__lte=0)
            return queryset.filter(query)
        return queryset
    
    def available_stocks_filter(self, queryset, name, value):
        """
        Filter to show only available stocks(quantity grater than zero).
        """
        if value:
            query = Q(current_quantity__gt=0)
            return queryset.filter(query)
        return queryset
