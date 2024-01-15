from rest_framework import serializers

from common.drf_custom import fields as custom_fields

from v1.products import models as product_models

from v1.supply_chains.serializers.supply_chain import SupplyChainSerializer

from v1.dynamic_forms import models as form_models


class UnitSerializer(serializers.ModelSerializer):
    """
    """
    id = custom_fields.IdencodeField(read_only=True)

    class Meta:
        """
        """
        model = product_models.Unit
        fields = ('id', 'name', 'code', 'factor', 'equivalent_kg',)


class ProductTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for product type.
    """
    id = custom_fields.IdencodeField(read_only=True)
    supply_chain = custom_fields.IdencodeField(
        serializer=SupplyChainSerializer, required=False)
    product_form = custom_fields.IdencodeField(read_only=True)
    batch_form = custom_fields.IdencodeField(read_only=True)
    internal_batch_form = custom_fields.IdencodeField(read_only=True)

    class Meta:
        """
        Meta Info.
        """
        model = product_models.Product
        fields = (
            'id', 'name', 'image', 'description', 'supply_chain', 
            'product_form', 'batch_form', 'internal_batch_form',
            )


class ProductSerializer(serializers.ModelSerializer):
    """
    """
    id = custom_fields.IdencodeField(read_only=True)
    supply_chain = custom_fields.IdencodeField(
        serializer=SupplyChainSerializer, required=False)
    unit = custom_fields.IdencodeField(
        serializer=UnitSerializer, required=False)
    product_type = custom_fields.IdencodeField(
        serializer=ProductTypeSerializer, read_only=True)
    product_specific_form = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission, read_only=True)

    class Meta:
        """
        """
        model = product_models.Product
        fields = (
            'id', 'name', 'image', 'description', 'supply_chain', 
            'unit', 'quantity', 'product_type', 'product_specific_form')


class ProductBaseSerializer(serializers.ModelSerializer):
    """
    """
    id = custom_fields.IdencodeField(read_only=True)
    supply_chain = custom_fields.IdencodeField(
        serializer=SupplyChainSerializer, required=False)
    unit = custom_fields.IdencodeField(
        serializer=UnitSerializer, required=False)
    product_type = serializers.CharField(
        source='product_type.name', default='', read_only=True)
    batch_form = custom_fields.IdencodeField(
        source='product_type.batch_form', default='', read_only=True)
    internal_batch_form = custom_fields.IdencodeField(
        source='product_type.internal_batch_form', default='', 
        read_only=True)
    product_specific_form = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission, read_only=True)
    class Meta:
        """
        """
        model = product_models.Product
        fields = (
            'id', 'name', 'image', 'description', 'supply_chain', 'unit', 
            'product_type', 'batch_form', 'internal_batch_form',
            'product_specific_form')
