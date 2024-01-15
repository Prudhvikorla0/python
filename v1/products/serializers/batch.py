from rest_framework import serializers

from django.utils.translation import gettext_lazy as _
from django.db import transaction as django_transaction
from common.drf_custom import fields as custom_fields
from django.utils import translation
from django.db.models import Sum, F

from base import session
from base import exceptions as base_exceptions
from utilities.translations import internationalize_attribute
from utilities.functions import encode

from v1.nodes import constants as node_consts
from v1.nodes import models as node_models

from v1.products import models as product_models
from v1.products.serializers import product as product_serializers

from v1.transactions import models as transaction_models
from v1.transactions import constants as txn_consts

from v1.claims import models as claim_models
from v1.claims.serializers.claim import BaseAttachedClaimSerializer

from v1.tenants import models as tenant_models

from v1.dynamic_forms import models as form_models


class BatchListSerializer(serializers.ModelSerializer):
    """
    Serializer to list batches.
    """

    id = custom_fields.IdencodeField(read_only=True)
    batch_id = serializers.IntegerField(source='number', read_only=True)
    product = custom_fields.IdencodeField(
        related_model=product_models.Product,
        serializer=product_serializers.ProductBaseSerializer,
        required=False)
    claims = custom_fields.ManyToManyIdencodeField(
        related_model=claim_models.BatchClaim, required=False,
        source='batch_claims', serializer=BaseAttachedClaimSerializer)
    unit = custom_fields.IdencodeField(
        serializer=product_serializers.UnitSerializer, read_only=True)
    batch_specific_form = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission, read_only=True)
    internal_form_submission = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission, allow_null=True, 
        required=False)

    class Meta:
        """
        Meta Info.
        """
        model = product_models.Batch
        fields = (
            'id', 'batch_id', 'product', 'name', 'claims', 'current_quantity',
            'initial_quantity', 'initial_quantity_kg', 'current_quantity_kg',
            'unit', 'tracker_link', 'batch_specific_form', 'internal_form_submission'
        )


class SourceBatchSerializer(serializers.Serializer):
    """ Serializer for validating source products in a transaction """

    batch = custom_fields.IdencodeField(
        related_model=product_models.Batch,
        serializer=BatchListSerializer)
    quantity = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3)

    class Meta:
        model = transaction_models.SourceBatch
        fields = ('batch', 'quantity', 'quantity_kg',)

    def validate(self, attrs):
        if attrs['batch'].current_quantity < attrs['quantity']:
            raise serializers.ValidationError(
                _("Batch quantity mismatch for {batch_id}").format(batch_id=attrs['batch'].idencode))
        return attrs


class SourceBatchListSerializer(serializers.ModelSerializer):
    """Serializer with sourcebatch list data"""

    transaction_id = serializers.IntegerField(
        source='transaction.number', read_only=True)
    date = custom_fields.UnixDateField(
        source='created_on', read_only=True)
    parent_txn_type = serializers.IntegerField(
        source='transaction.transaction_type', read_only=True)
    transaction_type = serializers.SerializerMethodField()
    transaction_partner = serializers.SerializerMethodField()
    unit = serializers.CharField(source='unit.name', read_only=True)

    class Meta:
        model = transaction_models.SourceBatch
        fields = (
            'transaction_id', 'parent_txn_type', 'transaction_type', 'date',
            'transaction_partner', 'quantity_kg', 'quantity', 'unit')

    def get_transaction_type(self, obj):
        """Method return transaction type"""

        if obj.transaction.transaction_type == \
                txn_consts.TransactionType.EXTERNAL:
            type = transaction_models.ExternalTransaction.objects.get(
                id=obj.transaction.id).type
        else:
            type = transaction_models.InternalTransaction.objects.get(
                id=obj.transaction.id).type
        return type

    def get_transaction_partner(self, obj):
        """Method return transaction type"""
        partner = ''
        if obj.transaction.transaction_type == \
                txn_consts.TransactionType.EXTERNAL:
            partner = transaction_models.ExternalTransaction.objects.get(
                id=obj.transaction.id).destination.name
        return partner


class BatchSerializer(serializers.ModelSerializer):
    """
    Serializer for batch details.
    """

    id = custom_fields.IdencodeField(read_only=True)
    product = product_serializers.ProductBaseSerializer(
        read_only=True)
    created_on = custom_fields.UnixDateField(read_only=True)
    source_data = serializers.SerializerMethodField()
    transaction_history = serializers.SerializerMethodField()
    claims = custom_fields.ManyToManyIdencodeField(
        serializer=BaseAttachedClaimSerializer,
        read_only=True, source='get_claims')
    unit = custom_fields.IdencodeField(
        read_only=True, serializer=product_serializers.UnitSerializer)
    batch_specific_form = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission, read_only=True)
    internal_form_submission = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission, allow_null=True, 
        required=False)
    date = serializers.DateField(
        required=False, 
        input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'),
        format='%d-%m-%Y')

    class Meta:
        """Meta Info."""

        model = product_models.Batch
        fields = (
            'id', 'number', 'name', 'product', 'created_on', 'initial_quantity',
            'initial_quantity_kg', 'current_quantity', 'current_quantity_kg',
            'source_data', 'transaction_history', 'claims', 'transaction_info',
            'unit', 'extra_info', 'tracker_link', 'batch_specific_form',
            'internal_form_submission', 'is_available', 'date',
        )

    def get_source_data(self, obj):
        """
        Information regarding the source transaction and source batches.
        """
        data = {}
        base_txn = obj.incoming_transactions.all().first()

        if base_txn:
            data['transaction_number'] = base_txn.number
            data['transaction_id'] = base_txn.idencode
            data['quantity'] = base_txn.source_quantity
            data['parent_txn_type'] = base_txn.transaction_type
            if base_txn.transaction_type == \
                    txn_consts.TransactionType.EXTERNAL:
                txn = transaction_models.ExternalTransaction.objects.get(
                    id=base_txn.id)
                data['child_txn_type'] = txn.type
                if txn.type == txn_consts.ExternalTransactionType.OUTGOING:
                    data['child_txn_type'] = txn_consts.ExternalTransactionType.INCOMING
            else:
                txn = transaction_models.InternalTransaction.objects.get(
                    id=base_txn.id)
                data['child_txn_type'] = txn.type

            data['source_company'] = txn.source_name
            data['country'] = txn.source_node.country.name
            data['province'] = txn.source_node.province.name
            source_batches = base_txn.source_batch_objects.all()
            data['source_batches'] = SourceBatchSerializer(
                source_batches, many=True).data
            source_products = list(source_batches.values('batch__product__name'
                ).annotate(total_quantity=Sum('quantity'), product=F('batch__product__name'), 
                unit=F('batch__product__unit__name'), product_id=F('batch__product__id')
                ).values('product_id','product','total_quantity','unit'))
            data['source_products'] = [
                {**source_product, 'product_id': encode(source_product['product_id'])} 
                    for source_product in source_products]
        return data

    def get_transaction_history(self, obj):
        """
        return transaction history
        """
        query = obj.outgoing_transaction_objects.all().order_by(
            '-transaction__date')
        return SourceBatchListSerializer(query, many=True).data
    
    def update(self, instance, validated_data):
        """
        """
        if validated_data.get('internal_form_submission',None):
            update_data = {
                "internal_form_submission": validated_data['internal_form_submission']
            }
            return super().update(instance, update_data)
        return instance
 

class CreateBatchSerializer(serializers.ModelSerializer):
    """
    Serializer for creating batch.
    """
    id = custom_fields.IdencodeField(read_only=True)
    product = custom_fields.IdencodeField(
        related_model=product_models.Product, write_only=True)
    quantity = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3, write_only=True)
    unit = custom_fields.IdencodeField(
        related_model=product_models.Unit, 
        serializer=product_serializers.UnitSerializer)
    number = serializers.IntegerField(read_only=True)
    batch_specific_form = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission, required=False, allow_null=True)
    internal_form_submission = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission, allow_null=True, 
        required=False)
    date = serializers.DateField(
        required=False, 
        input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'))

    class Meta:
        """Meta Info."""

        model = product_models.Batch
        fields = (
            'id',
            'product',
            'unit',
            'name',
            'quantity',
            'current_quantity',
            'initial_quantity',
            'initial_quantity_kg',
            'current_quantity_kg',
            'note', 
            'number', 
            'batch_specific_form',
            'internal_form_submission',
            'date',
        )

    def __init__(self, instance=None, data=serializers.empty, **kwargs):
        if data != serializers.empty:
            self.current_tenant = data.get(
                'current_tenant', session.get_current_tenant())
            self.current_node = data.get(
                'current_node', session.get_current_node())
            self.current_user = data.get(
                'current_user', session.get_current_user())
        else:
            self.current_tenant = session.get_current_tenant()
            self.current_node = session.get_current_node()
            self.current_user = session.get_current_user()

        super(CreateBatchSerializer, self).__init__(
            instance, data, **kwargs)

    @django_transaction.atomic
    def create(self, validated_data):
        validated_data['tenant'] = self.current_tenant
        validated_data['node'] = self.current_node
        validated_data['initial_quantity'] = validated_data['quantity']
        validated_data['current_quantity'] = validated_data['quantity']
        validated_data['risk_score'] = self.current_node.get_risk_score()
        validated_data.pop('quantity')

        non_producer_stock_creation = tenant_models.Tenant.objects.get(
            id=self.current_tenant.id).non_producer_stock_creation

        is_producer = node_models.Node.objects.get(
            id=self.current_node.id).is_producer

        if is_producer or non_producer_stock_creation:
            batch = product_models.Batch.objects.create(**validated_data)
            batch.name = _('Created {product} directly by {receiver}').format(
                product=validated_data['product'].name,
                receiver=validated_data['node'].name)
            s = _("Created {product} directly by {receiver}")  # DO NOT REMOVE. Added to register sentence in translation
            internationalize_attribute(
                obj=batch, field_name='name', text="Created {product} directly by {receiver}",
                params={
                    'product': validated_data['product'].name,
                    'receiver': validated_data['node'].name
                })
            batch.save()
            return batch
        else:
            raise base_exceptions.BadRequest(
                _("Non producers cannot create stock directly."))
