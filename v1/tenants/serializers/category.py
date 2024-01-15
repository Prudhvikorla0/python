"""serializers related to category."""

from rest_framework import serializers

from base import session

from common.drf_custom import fields as custom_fields

from v1.tenants import models as tenant_models


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category."""

    id = custom_fields.IdencodeField(read_only=True)
    
    class Meta:
        """Meta Info."""
        model = tenant_models.Category
        exclude = ('created_on', 'updated_on', 'creator', 'updater', 'tenant')

    def create(self, validated_data):
        """Create overrided to add creator and tenant."""
        validated_data['tenant'] = session.get_current_tenant()
        return super().create(validated_data)
