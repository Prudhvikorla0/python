"""Serializers for dashboard."""

from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

from base import exceptions
from base import session

from common.drf_custom import fields as custom_fields

from v1.dashboard import models as dashboard_models

from v1.supply_chains.models import SupplyChain


class DashboardSerializer(serializers.ModelSerializer):
    """Serializer for dashboard."""

    id = custom_fields.IdencodeField(read_only=True)

    class Meta:
        """Meta Info."""
        model = dashboard_models.DashboardTheme
        exclude = (
            'creator', 'updater', 'created_on', 'updated_on', 'tenant', 
            'is_default')

    def create(self, validated_data):
        """Create overrided to add creator."""
        tenant = session.get_current_tenant()
        if not tenant.dashboard_theming:
            raise exceptions.BadRequest(
                _('Tenant can not set dashboard theme.'))
        validated_data['tenant'] = tenant
        return super().create(validated_data)


class TrackerSerializer(serializers.ModelSerializer):
    """Serializer for dashboard."""

    id = custom_fields.IdencodeField(read_only=True)
    supply_chains = custom_fields.ManyToManyIdencodeField(
        related_model=SupplyChain, write_only=True, required=False)
    batch = custom_fields.IdencodeField()


    class Meta:
        """Meta Info."""
        model = dashboard_models.TrackerTheme
        exclude = (
            'creator', 'updater', 'created_on', 'updated_on', 'tenant', 
            'is_default', 'node',)

    def create(self, validated_data):
        """Create overrided to add creator."""
        tenant = session.get_current_tenant()
        if not tenant.ci_theming:
            raise exceptions.BadRequest(
                _('Tenant can not set tracker theme.'))
        validated_data['tenant'] = tenant
        validated_data['node'] = session.get_current_node()
        return super().create(validated_data)

    def to_representation(self, instance):
        """
        Overrided to change batch if batch in queryparam.
        """
        data = super().to_representation(instance)
        query_batch = self.context['request'].query_params.get('batch', None)
        if query_batch:
            data['batch'] = query_batch
        return data
