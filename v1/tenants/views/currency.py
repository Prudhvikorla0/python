"""Views realated to country model are stored here."""

from rest_framework import filters

from django_filters.rest_framework import DjangoFilterBackend

from base.views import IdDecodeModelViewSet
from base import session

from v1.tenants.serializers import currency as currency_serializers
from v1.tenants import models as tenant_models
from v1.tenants import filters as tenant_filters

# from v1.apiauth import permissions as auth_permissions


class CurrencyViewSet(IdDecodeModelViewSet):
    """
    View to list, create and update country data.
    """

    http_method_names = ['get', ]
    filterset_class = tenant_filters.CurrencyFilter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'code',]
    serializer_class = currency_serializers.CurrencySerializer

    def get_queryset(self):
        """ 
        Queryset overrided to filter currencies under 
        the logged-in user's tenant.
        """
        try:
            tenant = session.get_current_tenant()
            currencies = tenant.currencies.all()
        except:
            currencies = tenant_models.Currency.objects.all()
        return currencies
