"""Views related to category."""
from rest_framework import filters

from django.utils.translation import gettext_lazy as _

from base.views import IdDecodeModelViewSet
from base import session
from base import exceptions as base_exceptions

from base.response import SuccessResponse

from v1.tenants import models as tenant_models
from v1.tenants.serializers import category as category_serializers


class CategoryViewSet(IdDecodeModelViewSet):
    """
    View to list, create , update and delete category data.
    """

    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [filters.SearchFilter,]
    search_fields = ['name',]
    filterset_fields = ['type',]
    serializer_class = category_serializers.CategorySerializer

    def get_queryset(self):
        """ 
        Queryset overrided to filter categories of the logged-in user's tenant.
        """
        try:
            tenant = session.get_current_tenant()
            categories = tenant.categories.filter(
                is_active=True).select_related('updater', 'creator', 'tenant')
        except:
            categories = tenant_models.Category.objects.filter(
                is_active=True).select_related('updater', 'creator', 'tenant')
        return categories

    def destroy(self, request, *args, **kwargs):
        """
        Destroy overrided to to check node of the user and document are same.
        """
        tenant = session.get_current_tenant()
        category = self.get_object()
        if category.tenant != tenant:
            raise base_exceptions.BadRequest(_("Category can not be deleted."))
        category.delete()
        return SuccessResponse(_("Category deleted successfully."))
