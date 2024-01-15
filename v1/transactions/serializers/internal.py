from rest_framework import serializers

from django.db import transaction as django_transaction
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from django.utils import translation

from common.drf_custom import fields as custom_fields
from common import library as common_lib

from base import session
from base import exceptions
from utilities.translations import internationalize_attribute

from v1.products.serializers import batch as batch_serializers
from v1.products import models as prod_models
from v1.products.serializers import product as prod_serializers

from v1.transactions import models as trans_models
from v1.transactions.serializers.other import DestinationBatchSerializer
from v1.transactions import constants as transaction_consts

from v1.claims.serializers.claim import BaseAttachedClaimSerializer

from v1.dynamic_forms.models import FormSubmission


class InternalTransactionSerializer(serializers.ModelSerializer):
    """ Serializer to create internal transactions"""

    id = custom_fields.IdencodeField(read_only=True)
    creator = custom_fields.IdencodeField(read_only=True)
    transaction_id = serializers.CharField(source='number', read_only=True)
    transaction_id_for_user = serializers.CharField(
        source='number', read_only=True)
    source_batches = batch_serializers.SourceBatchSerializer(
        write_only=True, many=True)
    result_batches = DestinationBatchSerializer(
        write_only=True, many=True, required=False)
    unit = custom_fields.IdencodeField(
        related_model=prod_models.Unit, 
        serializer=prod_serializers.UnitSerializer)
    destination_quantity_kg = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3, read_only=True)
    destination_quantity = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3, read_only=True)
    source_quantity_kg = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3, read_only=True, required=False)
    source_quantity = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3, read_only=True, required=False)
    source_products = serializers.SerializerMethodField(
        'get_source_products', read_only=True)
    destination_products = serializers.SerializerMethodField(
        'get_destination_products', read_only=True)
    # source_batch_data = serializers.SerializerMethodField()
    # result_batch_data = serializers.SerializerMethodField()
    transaction_type = serializers.IntegerField(read_only=True)
    date = serializers.DateField(
        required=False, input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'))
    created_on = custom_fields.UnixTimeField(read_only=True)
    logged_date = serializers.DateField(
        read_only=True, input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'))
    claims = custom_fields.ManyToManyIdencodeField(
        serializer=BaseAttachedClaimSerializer,
        source='get_claims', read_only=True)
    submission_form = custom_fields.IdencodeField( 
        related_model=FormSubmission, required=False, allow_null=True)
    submission_form_mongo_id = serializers.CharField(required=False)
    status = serializers.IntegerField(required=False)
    transaction_hash = serializers.CharField(
        source='message_hash', read_only=True)

    class Meta:
        """
        Meta Info.
        """
        model = trans_models.InternalTransaction
        fields = (
            'id', 'mode', 'name', 'transaction_id', 'transaction_id_for_user', 'type',
            'date', 'source_batches', 'result_batches','destination_quantity', 
            'destination_quantity_kg', 'source_quantity', 'source_quantity_kg',
            'source_products', 'destination_products', 'transaction_type', 
            'unit', 'note', 'created_on', 'transaction_hash', 
            'status', 'logged_date', 'claims', 'submission_form', 'invoice_number', 
            'creator', 'submission_form_mongo_id', 'risk_score','risk_score_level',
        )

    def get_source_batch_data(self, instance):
        """ Source batches data"""
        return [
            {
                "product_id": source_batch.batch.product.idencode,
                "product_name": source_batch.batch.product.name,
                "supply_chain": source_batch.batch.product.supply_chain.name,
                "batch_id": source_batch.batch.idencode,
                "quantity": source_batch.quantity,
                "quantity_kg": source_batch.quantity_kg,
                "batch_number": source_batch.batch.number,
                "unit": source_batch.batch.unit.name
            } for source_batch in instance.source_batch_objects.all()
        ]

    def get_source_products(self, instance):
        """ Product data of source batches """
        data = []
        product_ids = instance.source_batch_objects.all().values_list(
            'batch__product', flat=True)
        products = prod_models.Product.objects.filter(id__in=product_ids)
        for product in products:
            prod_data = {
                "id": product.idencode, 
                "name": product.name, 
                "description": product.description, 
                "supply_chain": product.supply_chain.name
            }
            batches = instance.source_batch_objects.filter(
                batch__product=product)
            prod_data['unit'] = batches[0].unit.name
            prod_data['quantity'] = batches.aggregate(
                sum=Sum('quantity'))['sum']
            prod_data['quantity_kg'] = batches.aggregate(
                sum=Sum('quantity_kg'))['sum']
            data.append(prod_data)
        return data

    def get_destination_products(self, instance):
        """ Product data of destination batches """
        data = []
        product_ids = instance.result_batches.all().values_list(
            'product', flat=True)
        products = prod_models.Product.objects.filter(id__in=product_ids)
        for product in products:
            prod_data = {
                "id": product.idencode, 
                "name": product.name, 
                "description": product.description, 
                "supply_chain": product.supply_chain.name
            }
            batches = instance.result_batches.filter(
                product=product)
            prod_data['unit'] = batches[0].unit.name
            prod_data['quantity'] = batches.aggregate(
                sum=Sum('initial_quantity'))['sum']
            prod_data['quantity_kg'] = batches.aggregate(
                sum=Sum('initial_quantity_kg'))['sum']
            data.append(prod_data)
        return data

    def get_result_batch_data(self, instance):
        """ destination batches data"""
        return [
            {
                "product_id": result_batch.product.idencode,
                "product_name": result_batch.product.name,
                "supply_chain": result_batch.product.supply_chain.name,
                "batch_id": result_batch.idencode,
                "quantity": result_batch.initial_quantity,
                "quantity_kg": result_batch.initial_quantity_kg,
                "batch_number": result_batch.number,
                "unit": result_batch.unit.name, 
                "tracker_link": result_batch.tracker_link(),
                "batch_specific_form": result_batch.get_batch_specific_form_id()
            } for result_batch in instance.result_batches.all()
        ]

    def validate(self, attrs):
        """
        For loss transaction destination batch is not required,
        but for every other transactions, it is required.
        """
        current_user = session.get_current_user()
        if 'type' in attrs.keys():
            if attrs['type'] != transaction_consts.InternalTransactionType.LOSS:
                if 'result_batches' not in attrs:
                    raise exceptions.BadRequest(
                        _("result_batches is required."))
        return attrs

    def prepare_batches(self, validated_data):
        """
        If batches of multiple products are used for an internal
        transaction, some internal transaction will be created by
        the system to handle this.This will be different for
        different type of internal transactions.

        If product A, B, C are merged together as D,
            A will be converted to D
            B will be converted to D
            C will be converted to D
            Then the 3 output batches will be merged together

        If it is a processing transaction, it can have source batches
        of different types and different destination batches,
         so no system transaction will be created.

        """
        if validated_data['type'] != \
            transaction_consts.InternalTransactionType.MERGE:
            return validated_data
        product_ids = [
            i['batch'].product.id for i in validated_data['source_batches']]
        if len(set(product_ids)) == 1:
            return validated_data
        if len(validated_data['result_batches']) == 1:
            destination_batch = validated_data['result_batches'][0]
        else:
            raise exceptions.BadRequest(
                _("Merging transaction can have only one destination batch"))
        new_source_batch = []
        for batch in validated_data['source_batches']:
            if batch['batch'].product != destination_batch['product']:
                int_tran_data = {
                    'type': transaction_consts.InternalTransactionType.PROCESSING,
                    'mode': transaction_consts.TransactionMode.SYSTEM,
                    'note': validated_data.get('note', ""),
                    'source_batches': [{
                        'batch': batch['batch'].idencode,
                        'quantity': batch['quantity']
                    }],
                    'result_batches': [{
                        'product': destination_batch['product'].idencode,
                        'quantity': batch['quantity'],
                        'unit': batch['batch'].unit,
                        'batch_specific_form':destination_batch.get(
                            'batch_specific_form',None), 
                        'internal_form_submission': destination_batch.get(
                            'internal_form_submission',None), 
                    }], 
                    "unit": validated_data['unit']
                }
                if 'date' in validated_data:
                    int_tran_data['date'] = validated_data['date']
                int_tran_serializer = InternalTransactionSerializer(
                    data=int_tran_data, context=self.context)
                if not int_tran_serializer.is_valid():
                    raise serializers.ValidationError(
                        int_tran_serializer.errors)
                int_trans = int_tran_serializer.save()
                result_batch = int_trans.result_batches.first()
                new_source_batch.append({
                    'batch': result_batch,
                    'quantity': result_batch.initial_quantity
                })
            else:
                new_source_batch.append(batch)
        validated_data['source_batches'] = new_source_batch
        return validated_data

    @django_transaction.atomic
    def create(self, validated_data):
        """
        Create overrided to create internal transaction, source batches and 
            destination batches.
        """
        tenant = session.get_current_tenant()
        validated_data['tenant'] = tenant
        validated_data['status'] = \
            transaction_consts.TransactionStatus.APPROVED
        node = session.get_current_node()
        current_user = session.get_current_user()
        validated_data['transaction_type'] = \
            transaction_consts.TransactionType.INTERNAL
        validated_data['creator'] = current_user
        validated_data['updater'] = current_user
        validated_data['node'] = node
        validated_data = self.prepare_batches(validated_data)
        source_batches = validated_data.pop('source_batches')
        destination_batches = validated_data.pop(
            'result_batches', None)
        if 'mode' not in validated_data.keys():
            validated_data['mode'] = transaction_consts.TransactionMode.MANUAL
        transaction = trans_models.InternalTransaction.objects.create(
            **validated_data)
        source_quantity = 0
        destination_quantity = 0
        batch_risk_score = 0
        for batch_data in source_batches:
            batch = batch_data['batch']
            qty = batch_data['quantity']
            if batch.current_quantity < qty:
                raise serializers.ValidationError(
                    _("Not enough quantity in Batch"))
            batch.current_quantity -= qty
            batch.save()
            source_batch = trans_models.SourceBatch.objects.create(
                transaction=transaction, batch=batch, quantity=qty,
                unit=batch.unit,
                creator=validated_data['creator'],
                updater=validated_data['updater'])
            source_quantity += qty
            batch_risk_score += float(qty)*batch.risk_score
        final_batch_risk_score = batch_risk_score/float(source_quantity)
        if transaction.type != \
                transaction_consts.InternalTransactionType.LOSS:
            for product_data in destination_batches:
                result_batch = prod_models.Batch.objects.create(
                    tenant=tenant,
                    product=product_data['product'],
                    node=validated_data['node'],
                    initial_quantity=product_data['quantity'],
                    current_quantity=product_data['quantity'],
                    unit=product_data['unit'],
                    creator=validated_data['creator'],
                    updater=validated_data['updater'],
                    note=validated_data.get('note', ""), 
                    batch_specific_form=product_data.get(
                    'batch_specific_form', None), 
                    internal_form_submission=product_data.get(
                    'internal_form_submission', None), 
                    risk_score=final_batch_risk_score,
                    date=validated_data['date']
                )

                internationalize_attribute(
                    obj=result_batch, field_name='name', text=transaction.get_created_by)
                result_batch.save()

                destination_quantity += product_data['quantity']
                transaction.result_batches.add(result_batch)
            transaction.destination_quantity = destination_quantity
        transaction.source_quantity = source_quantity
        transaction.save()
        return transaction
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['result_batches'] = [
            {
                "product_id": result_batch.product.idencode,
                "product_name": result_batch.product.name,
                "supply_chain": result_batch.product.supply_chain.name,
                "batch_id": result_batch.idencode,
                "quantity": result_batch.initial_quantity,
                "quantity_kg": result_batch.initial_quantity_kg,
                "batch_number": result_batch.number,
                "unit": result_batch.unit.name, 
                "tracker_link": result_batch.tracker_link(),
                "batch_specific_form": result_batch.get_batch_specific_form_id(), 
                "internal_form_submission": result_batch.get_internal_form_submission_id(), 
            } for result_batch in instance.result_batches.all()
        ]
        data['source_batches'] = [
            {
                "product_id": source_batch.batch.product.idencode,
                "product_name": source_batch.batch.product.name,
                "supply_chain": source_batch.batch.product.supply_chain.name,
                "batch_id": source_batch.batch.idencode,
                "quantity": source_batch.quantity,
                "quantity_kg": source_batch.quantity_kg,
                "batch_number": source_batch.batch.number,
                "unit": source_batch.batch.unit.name
            } for source_batch in instance.source_batch_objects.all()
        ]
        return data


class InternalTransactionListSerializer(serializers.ModelSerializer):
    """ Serializer to create internal transactions"""

    id = custom_fields.IdencodeField(read_only=True)
    creator = custom_fields.IdencodeField(read_only=True)
    transaction_id = serializers.CharField(source='number', read_only=True)
    transaction_id_for_user = serializers.CharField(
        source='number', read_only=True)
    destination_quantity = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3, read_only=True, required=False)
    source_quantity = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3, read_only=True, required=False)
    destination_quantity_kg = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3, read_only=True, required=False)
    source_quantity_kg = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3, read_only=True, required=False)
    source_products = serializers.SerializerMethodField(
        'get_source_products', read_only=True)
    destination_products = serializers.SerializerMethodField(
        'get_destination_products', read_only=True)
    transaction_type = serializers.IntegerField(read_only=True)
    date = serializers.DateField(
        read_only=True, input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'))
    unit = custom_fields.IdencodeField(
        read_only=True, serializer=prod_serializers.UnitSerializer)
    class Meta:
        """
        Meta Info.
        """
        model = trans_models.InternalTransaction
        fields = (
            'id', 'transaction_id', 'transaction_id_for_user', 'type', 'date', 
            'destination_quantity', 'destination_quantity_kg', 
            'source_quantity', 'source_quantity_kg', 'source_products', 
            'destination_products', 'transaction_type', 'unit', 'creator',
            'risk_score', 'risk_score_level',
            )

    def get_source_products(self, instance):
        """ Product data of source batches """
        data = []
        product_ids = instance.source_batch_objects.all().values_list(
            'batch__product', flat=True)
        products = prod_models.Product.objects.filter(id__in=product_ids)
        for product in products:
            prod_data = {
                "id": product.idencode, 
                "name": product.name, 
                "description": product.description, 
                "supply_chain": product.supply_chain.name
            }
            batches = instance.source_batch_objects.filter(
                batch__product=product)
            prod_data['unit'] = batches[0].unit.name
            prod_data['quantity'] = batches.aggregate(
                sum=Sum('quantity'))['sum']
            prod_data['quantity_kg'] = batches.aggregate(
                sum=Sum('quantity_kg'))['sum']
            data.append(prod_data)
        return data

    def get_destination_products(self, instance):
        """ Product data of destination batches """
        data = []
        product_ids = instance.result_batches.all().values_list(
            'product', flat=True)
        products = prod_models.Product.objects.filter(id__in=product_ids)
        for product in products:
            prod_data = {
                "id": product.idencode, 
                "name": product.name, 
                "description": product.description, 
                "supply_chain": product.supply_chain.name
            }
            batches = instance.result_batches.filter(
                product=product)
            prod_data['unit'] = batches[0].unit.name
            prod_data['quantity'] = batches.aggregate(
                sum=Sum('initial_quantity'))['sum']
            prod_data['quantity_kg'] = batches.aggregate(
                sum=Sum('initial_quantity_kg'))['sum']
            data.append(prod_data)
        return data
