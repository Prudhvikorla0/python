"""Filters used in the tenant api."""

from django_filters import rest_framework as filters

from django.db.models import Q

import common.drf_custom.filters
from v1.tenants import models as tenant_models


class CurrencyFilter(filters.FilterSet):
    """
    Filterclass for currency-list api.
    """
    all = filters.BooleanFilter(method='all_filter')

    class Meta:
        """
        Meta Info.
        """
        model = tenant_models.Currency
        fields = ('name', 'code',)

    def all_filter(self, queryset, name, value):
        """
        Return all currencies
        """
        query = queryset
        if value:
            query = tenant_models.Currency.objects.all()
        return query

class ProvinceFilter(filters.FilterSet):
    """
    Filterclass for province
    """
    country = common.drf_custom.filters.IdencodeFilter(field_name='country')

    class Meta:
        model = tenant_models.Province
        fields = []


class RegionFilter(filters.FilterSet):
    """
    Filterclass for Region
    """
    province = common.drf_custom.filters.IdencodeFilter(field_name='province')

    class Meta:
        model = tenant_models.Region
        fields = []


class VillageFilter(filters.FilterSet):
    """
    Filterclass for province
    """
    region = common.drf_custom.filters.IdencodeFilter(field_name='region')

    class Meta:
        model = tenant_models.Village
        fields = []
