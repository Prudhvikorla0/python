from rest_framework import serializers

from django.db import models

from utilities.functions import decode

from v1.products import models as prod_models

from v1.tracker.serializers import common as common_serializers

from v1.tracker import operations as tracker_operations

from v1.nodes import constants as node_consts

from v1.transactions import models as txn_models
from v1.transactions import constants as txn_consts

from v1.supply_chains import models as sc_models

from v1.claims import models as claim_models


class BatchInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for basic batch info.
    """
    product = common_serializers.ProductBaseSerializer(
        read_only=True)
    claims = common_serializers.AttachedClaimBaseSerialier(
        read_only=True,many=True,source='get_claims')
    sc_info = serializers.SerializerMethodField()
    operations = serializers.SerializerMethodField()
    map_info = serializers.SerializerMethodField()

    batches = None
    target_batch = None

    def __init__(self, *args, **kwargs):
        """
        Initialize with commonly used data.
        """
        super(BatchInfoSerializer, self).__init__(*args, **kwargs)
        batch_ids,_ = tracker_operations.BatchSelection().track_batches(
            batch=self.instance, base_batch=True)
        self.batches = prod_models.Batch.objects.filter(
            id__in=batch_ids)

    def get_sc_info(self,obj):
        """
        Return supplychain related info of the current batch.
        """
        origin_batches = self.batches.filter(incoming_transactions=None).order_by(
            'node_id').distinct('node_id')
        batches = self.batches.order_by(
            'node_id').distinct('node_id')
        producers_batches = self.batches.filter(
                node__type=node_consts.NodeType.PRODUCER)
        info = {
            "origin_countries": origin_batches.values_list(
                'node__province__country__name',flat=True),
            "country_count": batches.order_by(
                'node__province__country__id').distinct(
                'node__province__country__id').count(), 
            "province_count": batches.order_by(
                'node__province__id').distinct(
                'node__province__id').count(), 
            "producers_count": producers_batches.count(),
            "actors_count": batches.count() - producers_batches.count()
        }
        return info
    
    def get_operations(self,batch):
        """
        Return operations(node types) of nodes in the current batch's 
        supply-chain.
        """
        operations = sc_models.Operation.objects.filter(
            nodes__id__in=self.batches.values_list('node__id',flat=True)
            ).order_by('position').distinct('position')
        operation_data = common_serializers.OperationBaseSerializer(
            operations,many=True).data
        return operation_data
    
    def get_map_info(self,batch):
        """
        Map data for the ci.
        """
        _,source_batches = tracker_operations.BatchSelection().track_batches(
            batch=self.instance, base_batch=True)
        _,ext_source_batches = tracker_operations.BatchSelection().track_batches(
            batch=self.instance, base_batch=True,external=True)
        ext_source_batches = ext_source_batches.order_by('-id').distinct('id')
        source_batches = source_batches.order_by('-id').distinct('id')
        node_info = []
        current_node_info = common_serializers.NodeSerializer(
                batch.node).data
        current_node_info['target'] = None
        current_node_info['is_end'] = True
        current_node_info['is_start'] = False
        current_node_info['batch'] = batch.idencode
        current_node_info['target_batch'] = None
        node_info.append(current_node_info)

        for source_batch in ext_source_batches:
            current_batch = source_batch.batch
            if not current_batch.node:
                node_info[-1]['is_start'] = True
                continue
            data = common_serializers.NodeSerializer(
                current_batch.node).data
            data['batch'] = current_batch.idencode
            data['target'] = source_batch.transaction.result_batches.first(
                ).node.idencode
            target_batch = source_batch.transaction.result_batches.first()
            try:
                target_batch = self.get_target_batch(
                    target_batch,source_batches,ext_source_batches).idencode
            except:
                target_batch = None
            data['target_batch'] = target_batch
            data['is_end'] = False
            data['is_start'] = False
            if not source_batch.batch.incoming_transactions.exists():
                data['is_start'] = True
            node_info.append(data)
        # if node_info[-1]['id'] != batch.node.idencode:
        #     pass
        return node_info
    
    def get_target_batch(self,target_batch,source_batches,external_batches):
        """
        Get target batch.
        """
        self.target_batch = target_batch
        while not (external_batches.filter(batch=self.target_batch).exists() or 
                   self.target_batch == self.instance):
            source_batch = source_batches.filter(
                batch=self.target_batch).order_by('id').first()
            if not source_batch:
                break
            self.target_batch = source_batch.transaction.result_batches.first()
        return self.target_batch

    class Meta:
        """
        Meta Info.
        """
        model = prod_models.Batch
        fields = (
            'product', 'claims', 'sc_info', 'operations',
            'map_info',)


class BatchChainSerializer(serializers.ModelSerializer):
    """
    """
    operation_info = serializers.SerializerMethodField()
    chain_info = serializers.SerializerMethodField()
    batches_info = serializers.SerializerMethodField()

    operation = sc_models.Operation.objects.none()
    tracked_batches = prod_models.Batch.objects.none()
    source_batches = txn_models.SourceBatch.objects.none()

    def __init__(self, *args, **kwargs):
        """
        Initialize with commonly used data.
        """
        super(BatchChainSerializer, self).__init__(*args, **kwargs)
        query_params = self.context.get('request').query_params
        self.operation = sc_models.Operation.objects.get(
            id=decode(
            query_params.get(
            'operation',self.instance.node.operation.idencode)))
        batch_ids, self.source_batches = tracker_operations.BatchSelection(
            ).track_batches(batch=self.instance, base_batch=True)
        self.source_batches = self.source_batches.filter(
            batch__node__operation=self.operation)
        self.tracked_batches = prod_models.Batch.objects.filter(
            id__in=batch_ids,node__operation=self.operation)

    def get_operation_info(self,batch):
        """
        Return operation details.
        """
        operation_info = common_serializers.OperationBaseSerializer(
            self.operation).data
        return operation_info
    
    def get_chain_info(self,batch):
        """
        Return information about the sc chain.
        """
        countries = self.tracked_batches.order_by(
            'node__province__country__id').distinct(
            'node__province__country__id').values_list(
            'node__province__country__name',flat=True)
        nodes_count = self.tracked_batches.order_by(
            'node_id').distinct('node_id').count()
        claims = claim_models.BatchClaim.objects.filter(
            batch__in=self.tracked_batches)
        claim_info = common_serializers.AttachedClaimBaseSerialier(
            claims,many=True).data
        info = {
            "countries": countries,
            "nodes_count": nodes_count,
            "claims": claim_info
        }
        return info
    
    def get_batches_info(self,batch):
        """
        Return batches info under the operation in the supply chain of the 
        given batch.
        """
        products = prod_models.Product.objects.filter(
            batches__in=self.tracked_batches).distinct()
        batches_info = []
        for product in products:
            txn_infos = []
            created_batches = self.tracked_batches.filter(
                incoming_transactions=None,
                product=product).order_by('created_on')
            if created_batches:
                txn_infos.append({
                    "main_txn": None,
                    "child_txn": None,
                    "quantity": created_batches.aggregate(
                        total=models.Sum('initial_quantity'))['total'],
                    "unit": product.unit.name,
                    'first_date': created_batches.first().created_on.date(),
                    "last_date": created_batches.last().created_on.date(),
                    "colors": None
                        })
            main_txn_types = txn_consts.TransactionType.values
            for main_txn_type in main_txn_types:
                child_txn_types = txn_consts.ExternalTransactionType.values
                if main_txn_type == txn_consts.TransactionType.INTERNAL:
                    child_txn_types = txn_consts.InternalTransactionType.values
                for child_txn_type in child_txn_types:
                    batches = self.tracked_batches.filter(
                        incoming_transactions__transaction_type=main_txn_type,
                        incoming_transactions__externaltransaction__type=child_txn_type,
                        product=product
                        ).order_by('incoming_transactions__date')
                    source_batches = self.source_batches.filter(
                            transaction__transaction_type=main_txn_type,
                            transaction__externaltransaction__type=child_txn_type,
                            batch__product=product
                            ).order_by('transaction__date')
                    if main_txn_type == txn_consts.TransactionType.INTERNAL:
                        batches = self.tracked_batches.filter(
                            incoming_transactions__transaction_type=main_txn_type,
                            incoming_transactions__internaltransaction__type=child_txn_type,
                            product=product
                            ).order_by('created_on')
                        source_batches = self.source_batches.filter(
                            transaction__transaction_type=main_txn_type,
                            transaction__internaltransaction__type=child_txn_type,
                            batch__product=product
                        ).order_by('transaction__date')
                    if batches:
                        if main_txn_type == txn_consts.TransactionType.EXTERNAL:
                            child_txn_type = txn_consts.ExternalTransactionType.INCOMING
                        txn_infos.append({
                            "main_txn": main_txn_type,
                            "child_txn": child_txn_type,
                            "quantity": batches.aggregate(
                                total=models.Sum('initial_quantity'))['total'],
                            "unit": product.unit.name,
                            'first_date': batches.first().incoming_transactions.first().date,
                            "last_date": batches.last().incoming_transactions.first().date,
                            "colors": None
                        })
                    if source_batches:
                        txn_infos.append({
                            "main_txn": main_txn_type,
                            "child_txn": child_txn_type,
                            "quantity": source_batches.aggregate(
                                total=models.Sum('quantity'))['total'],
                            "unit": product.unit.name,
                            'first_date': source_batches.first().transaction.date,
                            "last_date": source_batches.last().transaction.date,
                            "colors": None
                        })
            info = {
                "product": product.name,
                "txn_info": txn_infos
            }
            batches_info.append(info)
        return batches_info
        
    class Meta:
        """
        """
        model = prod_models.Batch
        fields = ('operation_info', 'chain_info', 'batches_info',)
