from rest_framework import serializers

from common.drf_custom import fields as custom_fields

from v1.products import models as prod_models
from v1.products.serializers import product as prod_serializers

from v1.dynamic_forms import models as form_models

from v1.transactions import models as txn_models


class DestinationBatchSerializer(serializers.Serializer):
    """ Serializer for validating destination products in a transaction """
    product = custom_fields.IdencodeField(
        related_model=prod_models.Product,
        serializer=prod_serializers.ProductBaseSerializer)
    quantity = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3)
    unit = custom_fields.IdencodeField(
        related_model=prod_models.Unit,
        serializer=prod_serializers.UnitSerializer)
    batch_specific_form = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission, 
        required=False, allow_null=True)
    internal_form_submission = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission, 
        required=False, allow_null=True)



class TxnBatchSerializer(serializers.ModelSerializer):
    """
    Serializer with basic details of a batch.
    """
    batch_id  = custom_fields.IdencodeField(read_only=True,source='id')
    batch_number = serializers.IntegerField(source='number',read_only=True)
    batch_quantity = serializers.FloatField(
        source='initial_quantity',read_only=True)
    batch_unit = serializers.CharField(source='unit.name',read_only=True)
    
    class Meta:
        """
        Meta Info.
        """
        model = prod_models.Batch
        fields = (
            'batch_id', 'batch_number', 'batch_quantity', 'batch_unit',
            'is_available', 'province',
            )


class TxnSourceBatchSerializer(serializers.ModelSerializer):
    """
    Serializer returns basic details about a source batch.
    """
    batch_id  = custom_fields.IdencodeField(
        read_only=True,source='batch.id')
    batch_number = serializers.IntegerField(
        source='batch.number',read_only=True)
    batch_quantity = serializers.FloatField(
        source='quantity',read_only=True)
    batch_unit = serializers.CharField(
        source='unit.name',read_only=True)
    is_available = serializers.BooleanField(
        source='batch.is_available')
    province = serializers.CharField(
        source='batch.province',read_only=True)
    
    class Meta:
        """
        Meta Info.
        """
        model = txn_models.SourceBatch
        fields = (
            'batch_id', 'batch_number', 'batch_quantity', 'batch_unit',
            'is_available', 'province',
            )
