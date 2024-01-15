from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from common.drf_custom import fields as custom_fields

from base import session

from v1.supply_chains import models as supply_models


class OperationSerializer(serializers.ModelSerializer):
    """
    """
    id = custom_fields.IdencodeField(read_only=True)
    tenant = custom_fields.IdencodeField(
        required=False, related_model='tenants.Tenant')

    class Meta:
        """
        """
        model = supply_models.Operation
        fields = ('id', 'name', 'node_type', 'tenant', 'image',)


class SupplyChainSerializer(serializers.ModelSerializer):
    """
    """
    id = custom_fields.IdencodeField(read_only=True)

    class Meta:
        """
        """
        model = supply_models.SupplyChain
        fields = ('id', 'name', 'image', 'description')

    def create(self, validated_data):
        validated_data['tenant'] = session.get_current_tenant()
        return super().create(validated_data)
