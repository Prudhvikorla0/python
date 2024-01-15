from rest_framework import filters

from base.views import IdDecodeModelViewSet
from base import session

from v1.products import models as product_models
from v1.products.serializers import product as product_serializers
from v1.products import filters as product_filter


class ProductViewSet(IdDecodeModelViewSet):
    """
    """

    filterset_class = product_filter.ProductFilter
    serializer_class = product_serializers.ProductSerializer
    http_method_names = ['get', 'patch',]

    def get_queryset(self):
        """
        """
        tenant = session.get_current_tenant()
        node = session.get_current_node()
        products = product_models.Product.objects.filter(
            tenant=tenant, is_active=True).select_related('supply_chain', 'unit')
        if node:
            products = products.filter(
                supply_chain__node_supplychains__node=node, 
                supply_chain__node_supplychains__is_active=True)
        return products


class UnitViewSet(IdDecodeModelViewSet):
    """
    """
    
    serializer_class = product_serializers.UnitSerializer
    http_method_names = ['get', 'post', 'patch']
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        """
        """
        tenant = session.get_current_tenant()
        units = tenant.units.filter(is_active=True)
        return units
