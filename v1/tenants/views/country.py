"""Views realated to country model are stored here."""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from sentry_sdk import capture_exception

from base.views import IdDecodeModelViewSet
from base import session

from v1.tenants.serializers import country as country_serializer
from v1.tenants import models as tenant_models
from v1.tenants import filters as tenant_filter

# from v1.apiauth import permissions as auth_permissions


class CountryViewSet(IdDecodeModelViewSet):
    """
    View to list, create and update country data.
    """

    http_method_names = ['get', ]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code', 'dial_code',]
    serializer_class = country_serializer.CountrySerializer

    def get_queryset(self):
        """ 
        Queryset overrided to filter countries of the logged-in user's tenant.
        """
        try:
            tenant = session.get_current_tenant()
            countries = tenant.countries.all()
        except Exception as e:
            capture_exception(e)
            countries = tenant_models.Country.objects.all()
        return countries.prefetch_related('currency', 'provinces', 'provinces__regions', 'provinces__regions__villages')


class ProvinceViewSet(IdDecodeModelViewSet):
    """
    View to list, create and update Province data.
    """

    http_method_names = ['get', ]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name',]
    filterset_class = tenant_filter.ProvinceFilter
    serializer_class = country_serializer.BaseProvinceSerializer
    queryset = tenant_models.Province.objects.all().prefetch_related(
        'regions', 'regions__villages')


class RegionViewSet(IdDecodeModelViewSet):
    """
    View to list, create and update Region data.
    """

    http_method_names = ['get', ]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name',]
    filterset_class = tenant_filter.RegionFilter
    serializer_class = country_serializer.BaseRegionSerializer
    queryset = tenant_models.Region.objects.all().prefetch_related('villages')


class VillageViewSet(IdDecodeModelViewSet):
    """
    View to list, create and update Village data.
    """

    http_method_names = ['get', 'post']
    filterset_class = tenant_filter.VillageFilter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name',]
    serializer_class = country_serializer.VillageSerializer
    queryset = tenant_models.Village.objects.all()
