"""Filters used in the app accounts."""

from django_filters import rest_framework as filters
from django.db.models import Q

from common.drf_custom import filters as custom_filters

from v1.bulk_templates import models as bulk_models


class TemplateFilter(filters.FilterSet):
    """
    Filter for Templates.
    """
    type = filters.NumberFilter()

    class Meta:
        model = bulk_models.Template
        fields = ['type']


class BulkUploadFilter(filters.FilterSet):
    """
    Filter for Templates.
    """
    type = filters.NumberFilter(field_name='template__type')
    supply_chain = custom_filters.IdencodeFilter()
    created_after = filters.DateFilter(field_name='created_on__date', lookup_expr='gte')
    created_before = filters.DateFilter(field_name='created_on__date', lookup_expr='lte')
    search = filters.CharFilter(method='search_filter')

    class Meta:
        model = bulk_models.BulkUpload
        fields = [
            'type', 'supply_chain', 'created_after', 'created_before', 'status',
            'search',
        ]

    def search_filter(self, queryset, name, value):
        query =Q(file_name__icontains=value) | Q(
            template__name__icontains=value) | Q(id__encoded=value)
        return queryset.filter(query)
