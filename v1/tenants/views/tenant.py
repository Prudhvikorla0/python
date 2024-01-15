from rest_framework import generics
from rest_framework import filters

from base import session
from base.views import IdDecodeModelViewSet

from v1.tenants.serializers import tenant as tenant_serializers
from v1.tenants import models as tenant_models


class ValidateTenantView(generics.CreateAPIView):
    """
    API to validate a Tenant.
    If not valid, the API will raise a 404
    If valid, the API return the id of the tenant
    """
    permission_classes = []
    serializer_class = tenant_serializers.ValidateTenantSubDomain


class TenantDetailView(generics.RetrieveAPIView):
    """"""

    serializer_class = tenant_serializers.TenantSerializer

    def get_object(self):
        """
        """
        return session.get_current_tenant()


class TagViewSet(IdDecodeModelViewSet):
    """
    Api for adding and updating tags.
    """

    queryset = tenant_models.Tag.objects.all()
    serializer_class = tenant_serializers.TagSerializer
    http_method_names = ['get', 'post', 'patch',]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        """
        Queryset overrided to return only tags of the current tenants.
        """
        tenant = session.get_current_tenant()
        return tenant_models.Tag.objects.filter(tenant=tenant)
