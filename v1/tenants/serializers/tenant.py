""" Serializerss for base tenant informations """
from rest_framework import serializers

from django.utils.translation import gettext_lazy as _
from django.conf import settings

from base import exceptions
from base import session

from common.drf_custom import fields as custom_fields

from v1.tenants import models as tenant_models


class ValidateTenantSubDomain(serializers.Serializer):
    """
    Serializer to validate tenant subdomain
    """

    tenant_subdomain = serializers.CharField()

    def validate_tenant_subdomain(self, value):
        if settings.ENTERPRISE_MODE:
            return tenant_models.Tenant.objects.get().idencode
        try:
            tenant = tenant_models.Tenant.objects.get(subdomain=value)
            return tenant.idencode
        except tenant_models.Tenant.DoesNotExist:
            raise exceptions.NoValueResponse(_("Invalid tenant"))

    def create(self, validated_data):
        return validated_data


class TenantSerializer(serializers.ModelSerializer):
    """
    """

    id = custom_fields.IdencodeField(read_only=True)
    node_form = custom_fields.IdencodeField(read_only=True)
    node_member_form = custom_fields.IdencodeField(read_only=True)
    internal_transaction_form = custom_fields.IdencodeField(read_only=True)
    external_transaction_form = custom_fields.IdencodeField(read_only=True)
    txn_enquiry_form = custom_fields.IdencodeField(read_only=True)
    dashboard_theme = custom_fields.IdencodeField(read_only=True)
    tracker_theme = serializers.SerializerMethodField()
    company_claim = serializers.BooleanField(source='node_claim')
    connection_template = custom_fields.IdencodeField(read_only=True)
    transaction_template = custom_fields.IdencodeField(read_only=True)
    env_data_form = custom_fields.IdencodeField(read_only=True)
    soc_data_form = custom_fields.IdencodeField(read_only=True)
    gov_data_form = custom_fields.IdencodeField(read_only=True)
    product_grouping = serializers.BooleanField(read_only=True)
    show_empty_batches = serializers.BooleanField(read_only=True)
    questionnaire = serializers.BooleanField(read_only=True)

    def get_tracker_theme(self, tenant):
        """Return tracker theme."""
        theme = None
        tracker_theme = tenant.tracker_theme()
        if tracker_theme:
            theme = tracker_theme.idencode
        return theme

    class Meta:
        """
        """
        model = tenant_models.Tenant
        fields = (
            'id', 'name', 'transaction', 'claim', 'purchase_order', 
            'ci_availability', 'custom_excel_template', 'dynamic_fields', 
            'connection_auto_approval', 'connection_disabling', 
            'transaction_auto_approval', 'transaction_rejection', 
            'mandatory_transaction_claims', 'dashboard_theming', 'ci_theming', 
            'blockchain_logging', 'node_anonymity', 'node_form', 
            'node_member_form', 'internal_transaction_form', 
            'external_transaction_form', 'txn_enquiry_form', 
            'dashboard_theme', 'tracker_theme', 'bulk_upload', 'company_claim', 
            'batch_claim', 'mobile_app', 'node_claim', 'connection_template', 
            'transaction_template', 'env_data_form', 'soc_data_form', 'gov_data_form', 
            'product_grouping', 'show_empty_batches', 'questionnaire'
            )


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for tags.
    """
    id = custom_fields.IdencodeField(read_only=True)

    class Meta:
        """
        Meta Info.
        """
        model = tenant_models.Tag
        fields = ('id', 'name')

    def validate(self, attrs):
        """
        Check the tag already exists or not in the tenant
        """
        tenant = session.get_current_tenant()
        name = attrs.get('name',None)
        if not name:
            name = self.instance.name
        old_tags = tenant.tags.filter(name=name)
        if old_tags.exists():
            raise exceptions.BadRequest(_("Tag already exists"))
        return super().validate(attrs)

    def create(self, validated_data):
        """
        Create overrided to add tenant.
        """
        validated_data['tenant'] = session.get_current_tenant()
        return super().create(validated_data)
