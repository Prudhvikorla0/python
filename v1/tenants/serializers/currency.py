"""Serializers related to currency related apis."""

from rest_framework import serializers

from common.drf_custom import fields as custom_fields

from v1.tenants import models as tenant_models


class CurrencySerializer(serializers.ModelSerializer):
    """
    Serializer for currency data.
    """

    id = custom_fields.IdencodeField(read_only=True)

    class Meta:
        """
        Meta Info.
        """
        model = tenant_models.Currency
        fields = ('id', 'name', 'code')
