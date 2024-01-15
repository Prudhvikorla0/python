from rest_framework import serializers

from v1.consumer_interface import models as ci_models


class   CIThemeSerializer(serializers.ModelSerializer):
    """Serializer for dashboard."""

    class Meta:
        """Meta Info."""
        model = ci_models.CITheme
        exclude = (
            'creator', 'updater', 'created_on', 'updated_on', 'tenant', 
            'is_default', 'is_current',)
