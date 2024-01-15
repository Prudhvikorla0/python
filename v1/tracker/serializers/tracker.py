"""Serializers for tracker apis"""

from rest_framework import serializers
from django.conf import settings

from common.drf_custom import fields as custom_fields
from utilities.functions import encode_list
from utilities.functions import decode
from base import session

from v1.products import models as product_models

from v1.nodes import constants as node_consts
from v1.nodes import models as node_models

from v1.tenants.serializers import country as country_serializers
from v1.transactions import models as txn_models
from v1.transactions import constants as txn_consts

from v1.tracker import operations
from django.db.models import F
from collections import ChainMap

from v1.claims import constants as claim_consts

from v1.tenants import constants as tenant_consts


class NodeSerializer(serializers.ModelSerializer):
    """
    """
    name = serializers.CharField(read_only=True)
    image = serializers.ImageField(read_only=True)
    operation = serializers.CharField(read_only=True, source='operation.name')
    country = custom_fields.CharListField(
        read_only=True, source='country.name')
    province = custom_fields.CharListField(
        read_only=True, source='province.name')
    latitude = serializers.CharField(read_only=True)
    longitude = serializers.CharField(read_only=True)

    
    class Meta:
        """
        """
        model = node_models.Node
        fields = (
            'name', 'image', 'operation', 'country', 'province', 
            'latitude', 'longitude'
            )
        ref_name='TrackerNodeSerializer'

    def to_representation(self, instance):
        """
        Overrided to set values on the basis of node data tranparency.
        """
        data = super().to_representation(instance)
        tenant = session.get_current_tenant()
        current_node = session.get_current_node()
        node_transparency = \
            tenant_consts.NodeDataTransparency.PARTIALY_TRANSPARENT
        if (tenant.node_data_transparency == node_transparency) and (
            instance not in current_node.get_connection_circle()):
            update_dict = {
                "name": "●●●●●●",
                "image": None,
            }
            data.update(update_dict)
        return data


class TransactionSerializer(serializers.ModelSerializer):
    """
    """

    number = serializers.CharField(read_only=True)
    main_transaction_type = serializers.IntegerField(
        read_only=True, source='transaction_type')
    transaction_type = serializers.IntegerField(
        source='child_transaction.type', read_only=True, default=None)
    sender = serializers.CharField(source='source_node.name', read_only=True)
    date = serializers.DateField(read_only=True)

    class Meta:
        """
        """
        model = txn_models.Transaction
        fields = (
            'number', 'main_transaction_type', 'transaction_type', 'sender', 
            'date')
        
    def to_representation(self, instance):
        """
        Overrided to set values on the basis of node data tranparency.
        """
        data = super().to_representation(instance)
        tenant = session.get_current_tenant()
        current_node = session.get_current_node()
        node_transparency = \
            tenant_consts.NodeDataTransparency.PARTIALY_TRANSPARENT
        if tenant.node_data_transparency == node_transparency:
            update_dict = {}
            if instance.source_node not in current_node.get_connection_circle():
                update_dict['sender'] = "●●●●●●"
            data.update(update_dict)
        return data


class ProductSerializer(serializers.ModelSerializer):
    """
    """
    
    name = serializers.CharField(read_only=True)
    image = serializers.ImageField(read_only=True)

    class Meta:
        """
        """
        model = product_models.Product
        fields = ('name', 'image',)
        ref_name='TrackerProductSerializer'


class BatchTrackSerializer(serializers.ModelSerializer):
    """
    """

    id = custom_fields.IdencodeField(read_only=True)
    product = ProductSerializer(read_only=True)
    initial_quantity = serializers.FloatField(read_only=True)
    current_quantity = serializers.SerializerMethodField()
    unit = serializers.CharField(source='unit.name', read_only=True)
    node = NodeSerializer(read_only=True)
    transaction_info = serializers.SerializerMethodField()
    claims = serializers.SerializerMethodField()
    source_batches = serializers.SerializerMethodField()


    def get_transaction_info(self, obj):
        """
        """
        try:
            txn = obj.incoming_transactions.first()
            info = {
                "main_transaction_type": txn.transaction_type, 
                "transaction_type": txn.child_transaction.type
            }
            if info['main_transaction_type'] == \
                txn_consts.TransactionType.EXTERNAL:
                info['transaction_type'] = \
                    txn_consts.ExternalTransactionType.OUTGOING
            return info
        except:
            return None

    def get_claims(self, obj):
        """
        """
        return obj.get_claims().filter(
            status=claim_consts.ClaimStatus.APPROVED
            ).values_list('claim__name', flat=True)

    def get_source_batches(self, obj):
        """
        """
        try:
            source_batch_ids = obj.source_batches_for_tracker().values_list(
                        'id', flat=True)
            source_batches = encode_list(source_batch_ids)
        except:
            source_batches = []
        return source_batches

    def get_current_quantity(self, obj):
        """
        """
        id = self.context.get('view').kwargs.get('pk')
        try:
            return txn_models.SourceBatch.objects.get(id=id).quantity
        except:
            return obj.initial_quantity


    class Meta:
        """
        """
        model = product_models.Batch
        fields = (
            'id', 'number', 'name', 'product', 'initial_quantity', 
            'current_quantity', 'claims', 'unit', 'node', 'transaction_info', 
            'source_batches',
            )
        
    def to_representation(self, instance):
        """
        Overrided to set values on the basis of node data tranparency.
        """
        data = super().to_representation(instance)
        tenant = session.get_current_tenant()
        current_node = session.get_current_node()
        node_transparency = \
            tenant_consts.NodeDataTransparency.PARTIALY_TRANSPARENT
        if (tenant.node_data_transparency == node_transparency) and (
            instance.node not in current_node.get_connection_circle()):
            update_dict = {
                "name": "●●●●●●"
            }
            data.update(update_dict)
        return data


class BatchSerializer(serializers.ModelSerializer):
    """
    """

    id = custom_fields.IdencodeField(read_only=True)
    product = serializers.CharField(source='product.name', read_only=True)
    number = serializers.CharField(read_only=True)
    initial_quantity = serializers.FloatField(read_only=True)
    send_quantity = serializers.SerializerMethodField()
    name = serializers.CharField(read_only=True)
    transaction_info = serializers.SerializerMethodField()
    node = custom_fields.IdencodeField(
        serializer=NodeSerializer, read_only=True)
    claims = serializers.SerializerMethodField()
    blockchain_info = serializers.SerializerMethodField()
    unit = serializers.CharField(source='unit.name', read_only=True)
    txn_text_info = serializers.SerializerMethodField()
    origin_info = serializers.SerializerMethodField()

    nxt_txn = None
    main_batch = None
    is_first = False

    def __init__(self, *args, **kwargs):
        """
        """
        super(BatchSerializer, self).__init__(*args, **kwargs)
        main_batch = self.context['request'].query_params.get('main_batch', None)
        batch = product_models.Batch.objects.get(
            id=self.context.get('view').kwargs.get('pk', None))
        if main_batch == batch.idencode:
            self.is_first = True
        if main_batch:
            self.main_batch = product_models.Batch.objects.get(id=decode(main_batch))
            batches,_ = operations.BatchSelection().track_batches(
                batch=self.main_batch, base_batch=True)
            batches = sorted(batches)
        try:
            nxt_batch = txn_models.Transaction.objects.filter(
                source_batches=main_batch,result_batches=batches
                ).order_by('id').first()
        except:
            nxt_batch = None
        txn_list = batch.outgoing_transaction_objects.all().values_list('transaction')
        txns = txn_models.Transaction.objects.filter(
            id__in=txn_list)
        if nxt_batch:
            txns = txns.filter(result_batches__id=nxt_batch)
        if txns:
            self.nxt_txn = txns.first()

    def get_origin_info(self, obj):
        """
        Returns 'origin' as true if created. Also returns its respective colour
        for tracker.
        """

        info = {
            'is_origin': True,
            'colors' : txn_consts.origin_transaction_colours
        }
        if obj.incoming_transactions.all():
            info['is_origin'] = False
            info['colors'] = None
            return info
        return info

    def get_txn_text_info(self, obj):
        """
        """
        info = None
        if self.nxt_txn or self.main_batch == obj:
            txn = self.nxt_txn
            if self.main_batch == obj:
                txn = obj.incoming_transactions.first()
            info = {
                "node": txn.destination_node.name, 
                "main_txn_type": txn.transaction_type, 
                "child_txn_type": txn.child_transaction.type, 
                "colors": None, 
                "is_first":self.is_first
            }
            if txn.transaction_type == \
                txn_consts.TransactionType.EXTERNAL:
                info['child_txn_type'] = \
                    txn_consts.ExternalTransactionType.OUTGOING
                if self.is_first:
                    info['child_txn_type'] = \
                    txn_consts.ExternalTransactionType.INCOMING
                info['colors'] = txn_consts.external_transaction_colours[info['child_txn_type']]
            else:
                info['colors'] =txn_consts.internal_transaction_colours[info['child_txn_type']]
        return info

    def get_transaction_info(self, obj):
        """
        """
        try:
            txn = obj.incoming_transactions.first()
            data = TransactionSerializer(txn).data
            if txn.transaction_type == \
                txn_consts.TransactionType.EXTERNAL:
                data['transaction_type'] = \
                    txn_consts.ExternalTransactionType.OUTGOING
                if self.is_first:
                    data['transaction_type'] = \
                    txn_consts.ExternalTransactionType.INCOMING
            return data
        except:
            return None

    def get_claims(self, obj):
        """
        Get claims based on batch
        """
        data = []
        batch_claims = obj.get_claims().filter(
            status=claim_consts.ClaimStatus.APPROVED)
        for batch_claim in batch_claims:
            info = {}
            info['evidence'] = None
            if batch_claim.criteria.first():
                form_field_values = batch_claim.criteria.first().form_submission.field_values.all().annotate(
                    label=F('field__label'), width=F('field__width'), type=F('field__type'), options_selected=F('selected_options__name')).values(
                    'label', 'type', 'value', 'file', 'options_selected', 'width')
                for value in form_field_values:
                    if value['file']:
                        value['file'] = f"https:{settings.MEDIA_URL}{value['file']}"
                info.update({'evidence':form_field_values})
            info['name'] = batch_claim.claim.name
            info['description'] = batch_claim.claim.description
            data.append(info)
        return data

    def get_blockchain_info(self, obj):
        """
        """
        info = {
            "txn_hash": "Pending",
            "source_address": "Pending", 
            "target_address": "Pending"
        }
        return info

    def get_send_quantity(self, obj):
        """
        """
        try:
            if self.main_batch == obj:
                return obj.initial_quantity
            txn = self.nxt_txn
            if not self.nxt_txn:
                txn = obj.outgoing_transactions.first()
            return txn_models.SourceBatch.objects.get(
                transaction=txn, batch=obj).quantity
        except:
            return obj.initial_quantity

    class Meta:
        """
        """
        model = product_models.Batch
        fields = (
            'id', 'number', 'name', 'product', 'initial_quantity', 'claims', 
            'unit', 'node', 'transaction_info', 'blockchain_info', 
            'send_quantity', 'txn_text_info', 'origin_info', 'created_on'
            )
        ref_name='StockSerializer'

    def to_representation(self, instance):
        """
        Overrided to set values on the basis of node data tranparency.
        """
        data = super().to_representation(instance)
        data['is_anonymous'] = False
        tenant = session.get_current_tenant()
        current_node = session.get_current_node()
        node_transparency = \
            tenant_consts.NodeDataTransparency.PARTIALY_TRANSPARENT
        if (tenant.node_data_transparency == node_transparency):
            txn_text_info = data.get('txn_text_info', None)
            block_chain_info = data.get('txn_text_info', None)
            if txn_text_info and (
                    self.nxt_txn and 
                    self.nxt_txn.destination_node not in current_node.get_connection_circle()
                    ):
                txn_text_info['node'] = "●●●●●●"
            if instance.node not in current_node.get_connection_circle():
                block_chain_info = {
                "txn_hash": "●●●●●●",
                "source_address": "●●●●●●",
                "target_address": "●●●●●●",
                }
                update_dict = {
                    "name": "●●●●●●",
                    "claims": instance.batch_claims.filter(
                        status=claim_consts.ClaimStatus.APPROVED).annotate(
                        name=F('claim__name'), 
                        description=F('claim__description')).values(
                        'name', 'description'), 
                    "blockchain_info": block_chain_info,
                    "txn_text_info": txn_text_info,
                    "is_anonymous": True
                }
                data.update(update_dict)
        return data


class TrackerInfoSerializer(serializers.ModelSerializer):
    """    
    """
    
    batch_number = serializers.IntegerField(read_only=True, source='number')
    name = serializers.CharField(source='node.name')
    image = serializers.ImageField(read_only=True, source='node.image')
    operation = serializers.CharField(
        read_only=True, source='node.operation.name')
    country = custom_fields.CharListField(
        read_only=True, source='node.country.name')
    province = custom_fields.CharListField(
        read_only=True, source='node.province.name')
    latitude = serializers.CharField(
        read_only=True, source='node.latitude')
    longitude = serializers.CharField(
        read_only=True, source='node.longitude')


    class Meta:
        """
        """
        model = product_models.Batch
        fields = (
            'batch_number', 'name', 'image', 'operation', 
            'country', 'province', 'latitude', 'longitude'
            )
        
    def to_representation(self, instance):
        """
        Overrided to set values on the basis of node data tranparency.
        """
        data = super().to_representation(instance)
        tenant = session.get_current_tenant()
        current_node = session.get_current_node()
        node_transparency = \
            tenant_consts.NodeDataTransparency.PARTIALY_TRANSPARENT
        if (tenant.node_data_transparency == node_transparency) and (
            instance.node not in current_node.get_connection_circle()):
            update_dict = {
                "name": "●●●●●●", 
                "image": None,
            }
            data.update(update_dict)
        return data
