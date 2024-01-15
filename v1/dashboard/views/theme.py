"""Views under dashboard are saved here."""

from rest_framework import generics

from base.views import IdDecodeModelViewSet
from base import session

from v1.dashboard.serializers import theme as theme_serializers
from v1.dashboard import models as dashboard_models


class DashBoardThemeView(generics.RetrieveAPIView):
    """Api to retrieve dashboard data."""

    serializer_class = theme_serializers.DashboardSerializer
    permission_classes = ()
    authentication_classes = ()

    def get_object(self):
        """Overrided to retrieve only specific tenants dashboard."""
        try:
            dashboard_theme = dashboard_models.DashboardTheme.objects.get(
                tenant__id=self.kwargs['id'], is_default=True)
        except:
            dashboard_theme = None
        return dashboard_theme


class TrackerThemeView(generics.RetrieveAPIView):
    """Api to retrieve tracker data."""

    serializer_class = theme_serializers.TrackerSerializer
    permission_classes = ()
    authentication_classes = ()

    def get_object(self):
        """Overrided to retrieve only specific tenants tracker theme."""
        try:
            tracker_theme = dashboard_models.TrackerTheme.objects.get(
                tenant__id=self.kwargs['id'], name=self.kwargs['name'])
        except:
            tracker_theme = None
        return tracker_theme
