"""Views related dashboard apis are stored here."""

from rest_framework import generics
from rest_framework.views import APIView

from base import session
from base.response import SuccessResponse

from v1.dashboard.serializers import dashboard as dashboard_serializers

from v1.products import models as prod_models


class ConnectionStatsView(generics.RetrieveAPIView):
    """Connection related statistical data return this api."""

    serializer_class = dashboard_serializers.ConnectionStatSerializer

    def get_object(self):
        """Return current useres selected node."""
        node = session.get_current_node()
        return node


class SupplierStatsView(generics.RetrieveAPIView):
    """Supplier Connection related statistical data return this api."""

    serializer_class = dashboard_serializers.SupplierStatSerializer

    def get_object(self):
        """Return current useres selected node."""
        node = session.get_current_node()
        return node

class ProductStatsView(generics.RetrieveAPIView):
    """Supplier Prduct related statistical data return this api."""

    serializer_class = dashboard_serializers.ProductInfoSerializer
    queryset = prod_models.Product.objects.all()

class ESGStatsView(generics.RetrieveAPIView):
    """Suppliers esg score data return this api."""

    serializer_class = dashboard_serializers.ESGStatSerializer

    def get_object(self):
        """Return current useres selected node."""
        node = session.get_current_node()
        return node
    

class RiskStatsView(generics.RetrieveAPIView):
    """Risk statistical data return this api."""

    serializer_class = dashboard_serializers.RiskStatSerializer

    def get_object(self):
        """Return current useres selected node."""
        node = session.get_current_node()
        return node
