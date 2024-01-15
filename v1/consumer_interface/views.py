from rest_framework import generics

from base import exceptions, response

from v1.tenants import models as tenant_models

from v1.consumer_interface.serializers import theme as ci_theme_serializers
from v1.consumer_interface.serializers import dynamic_data as ci_data_serializers

from v1.products import models as prod_models


class CISectionsView(generics.RetrieveAPIView):
    """
    """
    authentication_classes = []
    permission_classes = []

    def get_object(self):
        """
        Only returns the specified batch.
        """
        try:
            tenant = tenant_models.Tenant.objects.get(
                id=self.kwargs['pk'])
        except:
            raise exceptions.NotFound("Tenant does not exist.")
        return tenant
    
    def retrieve(self, request, *args, **kwargs):
        """
        """
        tenant = self.get_object()
        section_data = tenant.ci_section_data()
        return response.SuccessResponse(section_data)


class CIThemeView(generics.RetrieveAPIView):
    """Api to retrieve ci theme data."""

    authentication_classes = []
    permission_classes = []
    serializer_class = ci_theme_serializers.CIThemeSerializer

    def get_object(self):
        """Overrided to retrieve only specific tenants ci theme."""
        try:
            tenant = tenant_models.Tenant.objects.get(
                id=self.kwargs['pk'])
            ci_theme = tenant.ci_theme()
            return ci_theme
        except:
            raise exceptions.NotFound("Tenant does not exist.")


class BatchInfoView(generics.RetrieveAPIView):
    """
    Api to get information about a specific batch.
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = ci_data_serializers.BatchInfoSerializer

    def get_object(self):
        """
        Only returns the specified batch.
        """
        try:
            batch = prod_models.Batch.objects.get(
                id=self.kwargs['pk'])
        except:
            raise exceptions.NotFound("Batch does not exist.")
        return batch


class BatchChainInfoView(generics.RetrieveAPIView):
    """
    Api return chain info of a batch.
    The contribution of a specific type of nodes into the chain.
    The type is taken as operation queryparm in the url.
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = ci_data_serializers.BatchChainSerializer

    def get_object(self):
        """
        Only returns the specified batch.
        """
        try:
            batch = prod_models.Batch.objects.get(
                id=self.kwargs['pk'])
        except:
            raise exceptions.NotFound("Batch does not exist.")
        return batch
