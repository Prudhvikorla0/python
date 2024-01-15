
from rest_framework import serializers
from django.db import transaction as django_transaction
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils import translation
from django.db.models import Q

from common.drf_custom import fields as custom_fields
from common.library import _datetime_to_unix

from base import session
from base import exceptions as base_exceptions
from utilities.translations import internationalize_attribute

from v1.transactions import models as transaction_models
from v1.transactions import constants as transaction_consts
from v1.transactions.serializers import internal as int_txn_serializers

from v1.products import models as product_models
from v1.products.serializers import batch as batch_serializers
from v1.products.serializers.product import ProductBaseSerializer, UnitSerializer

from v1.nodes.serializers import node as node_serializers
from v1.nodes import models as node_models
from v1.nodes import constants as node_consts

from v1.tenants import models as tenant_models
from v1.tenants.serializers import currency as currency_serializer

from v1.claims.serializers.claim import BaseAttachedClaimSerializer
from v1.claims import constants as claim_consts

from v1.dynamic_forms.models import FormSubmission


class ExternalTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for external transaction.
    """

    id = custom_fields.IdencodeField(read_only=True)
    creator = custom_fields.IdencodeField(read_only=True)
    name = serializers.CharField(read_only=True)
    transaction_id = serializers.CharField(source='number', read_only=True)
    transaction_id_for_user = serializers.CharField(
        source='number', read_only=True)
    product = custom_fields.IdencodeField(
        related_model=product_models.Product, write_only=True)
    quantity = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3, write_only=True)
    unit = custom_fields.IdencodeField(
        related_model=product_models.Unit, serializer=UnitSerializer)
    node = custom_fields.IdencodeField(
        related_model=node_models.Node, write_only=True, allow_null=True, 
        required=False)
    batches = batch_serializers.SourceBatchSerializer(
        write_only=True, many=True, required=False)
    source = custom_fields.IdencodeField(
        serializer=node_serializers.NodeSerializer, 
        related_model=node_models.Node, read_only=True)
    destination = custom_fields.IdencodeField(
        read_only=True, serializer=node_serializers.BasicNodeSerializer)
    products = ProductBaseSerializer(many=True, read_only=True)
    source_batches = serializers.SerializerMethodField()
    result_batches = custom_fields.ManyToManyIdencodeField(
        serializer=batch_serializers.BatchListSerializer, read_only=True)
    date = serializers.DateField(
        required=False, input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'))
    currency = custom_fields.IdencodeField(
        related_model=tenant_models.Currency, required=False, 
        serializer=currency_serializer.CurrencySerializer)
    logged_date = serializers.DateField(
        read_only=True, input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'))
    force_create = serializers.BooleanField(
        write_only=True, default=False, required=False)
    claims = custom_fields.ManyToManyIdencodeField(
        serializer=BaseAttachedClaimSerializer,
        source='get_claims', read_only=True)
    purchase_order = custom_fields.IdencodeField(
        related_model=transaction_models.PurchaseOrder, required=False, 
        allow_null=True)
    transaction_type = serializers.IntegerField(read_only=True)
    submission_form = custom_fields.IdencodeField( 
        related_model=FormSubmission, required=False, allow_null=True)
    submission_form_mongo_id = serializers.CharField(required=False)
    status = serializers.IntegerField(required=False)
    reversal_txn_info = serializers.SerializerMethodField()
    transaction_hash = serializers.CharField(
        source='message_hash', read_only=True)
    rejection_reason = serializers.CharField(read_only=True)
    batch_specific_form = custom_fields.IdencodeField(
        related_model=FormSubmission, 
        required=False, allow_null=True, allow_blank=True)
    internal_form_submission = custom_fields.IdencodeField(
        related_model=FormSubmission, 
        required=False, allow_null=True, allow_blank=True)
    # upload_timestamp = serializers.CharField(
    #     read_only=True)

    class Meta:
        """
        Meta Info.
        """

        model = transaction_models.ExternalTransaction
        fields = (
            'id', 'name', 'transaction_id', 'transaction_id_for_user',
            'transaction_type', 'date', 'batches', 'price', 'currency', 
            'type', 'destination', 'result_batches', 'source', 
            'source_batches', 'products', 'node', 'status', 'product', 
            'quantity', 'unit', 'note', 'claims', 'logged_date', 
            'force_create', 'purchase_order', 'submission_form', 
            'reversal_txn_info', 'extra_info', 'transaction_hash', 
            'invoice_number', 'upload_timestamp', 'rejection_reason',
            'creator', 'submission_form_mongo_id', 'batch_specific_form',
            'internal_form_submission', 'risk_score', 'risk_score_level',
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

        super(ExternalTransactionSerializer, self).__init__(
            instance, data, **kwargs)

    def validate(self, attrs):
        """
        validate the nodes.
        """
        if not self.instance and attrs['type'] != \
            transaction_consts.ExternalTransactionType.INCOMING_WITHOUT_SOURCE:
            if 'node' not in attrs or attrs['node'] not in \
                    self.current_node.connections.all():
                raise base_exceptions.BadRequest(
                    _("Nodes are not connected."))
            if attrs['type'] == \
                transaction_consts.ExternalTransactionType.INCOMING and \
                    attrs['node'].type != node_consts.NodeType.PRODUCER:
                raise base_exceptions.BadRequest(
                    _("Selected node is not producer."))
        return super().validate(attrs)

    def get_buyer_supplier(self, node):
        """
        return buyer and supplier.
        """
        if self.validated_data['type'] in [
            transaction_consts.ExternalTransactionType.OUTGOING, 
            transaction_consts.ExternalTransactionType.REVERSAL
            ]:
            supplier = self.current_node
            buyer = node
        else:
            supplier = node
            buyer = self.current_node
        return buyer, supplier

    def get_source_batches(self, obj):
        """Source batch data."""
        source_batches = obj.source_batch_objects.all()
        batch_data = []
        for source_batch in source_batches:
            data = batch_serializers.BatchListSerializer(
                source_batch.batch).data
            data.pop("initial_quantity")
            data.pop("initial_quantity_kg")
            data.pop("current_quantity")
            data.pop("current_quantity_kg")
            data['quantity'] = source_batch.quantity
            data['quantity_kg'] = source_batch.quantity_kg
            batch_data.append(data)
        return batch_data

    def get_reversal_txn_info(self, obj):
        """
        if the transaction is reverse transaction then the parent 
        transaction information returned.
        """
        parent_txn_data = {}
        if obj.type == transaction_consts.ExternalTransactionType.REVERSAL:
            txn = obj.source_batches.first().incoming_transactions.first()
            parent_txn_data = {
                "id": txn.idencode, 
                "transaction_id": txn.number, 
                "date": txn.date
            }
        elif obj.status == transaction_consts.TransactionStatus.DECLINED:
            txn = obj.result_batches.first().outgoing_transactions.first()
            parent_txn_data = {
                "id": txn.idencode, 
                "transaction_id": txn.number, 
                "date": txn.date
            }
        return parent_txn_data

    def prepare_batches(self, validated_data):
        """
        Method creates internal transactions and batches if required.
        """
        incoming_txns = [
            transaction_consts.ExternalTransactionType.INCOMING, 
            transaction_consts.ExternalTransactionType.INCOMING_WITHOUT_SOURCE
        ]
        if validated_data['type'] in incoming_txns:
            risk_score = 0
            if validated_data.get('source',None):
                risk_score = validated_data['source'].get_risk_score()
            batch = product_models.Batch.objects.create(
                node=validated_data['source'],
                product=validated_data['product'],
                initial_quantity=validated_data['quantity'],
                current_quantity=validated_data['quantity'],
                unit=validated_data['unit'],
                tenant=self.current_tenant, 
                batch_specific_form=validated_data.get('batch_specific_form', None),
                risk_score=risk_score,
                date=validated_data['date']
            )
            s = _("Created for transfering {product} to {receiver}")  # DO NOT REMOVE. Added to register sentence in translation
            internationalize_attribute(
                obj=batch, field_name='name', text='Created for transfering {product} to {receiver}',
                params={
                    'product': validated_data['product'].name,
                    'receiver': validated_data['destination'].name
                })
            batch.save()
            validated_data['batch'] = {
                'batch': batch,
                'quantity': batch.initial_quantity
            }
        else:
            batches = validated_data.get('batches', None)
            if len(batches) > 1:
                source_batches = [
                    {'batch': i['batch'].idencode,
                    'quantity': i['quantity']}
                    for i in batches]
                int_tran_data = {
                    'type':
                        transaction_consts.InternalTransactionType.PROCESSING,
                    'mode': transaction_consts.TransactionMode.SYSTEM,
                    'source_batches': source_batches,
                    'note': validated_data.get('note', ""),
                    'result_batches': [{
                        'product': validated_data['product'].idencode,
                        'quantity': validated_data['quantity'],
                        'unit': validated_data['unit'],
                        'batch_specific_form': validated_data.get('batch_specific_form', None)
                    }],
                    'unit': validated_data['unit']
                }
                batch_products = { 
                    batch['batch'].product.id for batch in batches }
                batch_products.remove(validated_data['product'].id)
                if len(batch_products) == 0:
                    int_tran_data['type'] = \
                        transaction_consts.InternalTransactionType.MERGE
                if 'date' in validated_data:
                    int_tran_data['date'] = validated_data['date']
                int_tran_serializer = \
                    int_txn_serializers.InternalTransactionSerializer(
                    data=int_tran_data, context=self.context)
                if not int_tran_serializer.is_valid():
                    raise serializers.ValidationError(
                        int_tran_serializer.errors)
                int_trans = int_tran_serializer.save()
                result_batch = int_trans.result_batches.first()
                validated_data['batch'] = {
                    'batch': result_batch,
                    'quantity': result_batch.initial_quantity
                }
            else:
                validated_data['batch'] = batches[0]
        return validated_data

    @staticmethod
    def update_purchase_order(purchase_order, transaction, user_approve=False):
        """Function updates purchase with transaction."""
        txn_status = [
            transaction_consts.TransactionStatus.CREATED, 
            transaction_consts.TransactionStatus.ON_HOLD]
        if not purchase_order.transactions.filter(
            status__in=txn_status).exists() and \
            purchase_order.sent_quantity >= purchase_order.quantity:
            purchase_order.approve()
        elif user_approve:
            return True
        else:
            purchase_order.sent_quantity += transaction.source_quantity
            if purchase_order.sent_quantity >= purchase_order.quantity:
                purchase_order.sent_quantity = purchase_order.quantity
                if not purchase_order.transactions.filter(
                    status__in=txn_status).exists():
                    purchase_order.approve()
            else:
                purchase_order.status = \
                    transaction_consts.PurchaseOrderStatus.PARTIAL
            purchase_order.save()
        return True

    @staticmethod
    def create_inherited_claims(
        source_batches=None, result_batch=None, transaction=None):
        """
        Creates inherited claims for the transaction of type reversal
        """
        for source_batch in source_batches:
            batch_claims = source_batch['batch'].batch_claims.filter(
                Q(attached_via=claim_consts.ClaimAttachedVia.INHERITANCE)|Q(
                    status=claim_consts.ClaimStatus.APPROVED)).distinct()
            for batch_claim in batch_claims:
                new_batch_claim = batch_claim
                new_batch_claim.id = None
                new_batch_claim.pk = None
                new_batch_claim.batch = result_batch
                if batch_claim.transaction:
                    new_batch_claim.transaction = transaction
                new_batch_claim.save()
                for criterion in batch_claim.criteria.all():
                    new_criterion = criterion
                    new_criterion.id = None
                    new_criterion.pk = None
                    new_criterion.batch_claim = batch_claim
                    new_criterion.save()
        return True

    @django_transaction.atomic
    def create(self, validated_data):
        """
        Create overrided to create transaction , source batches 
        and destination batches.
        """
        current_user = self.current_user
        validated_data['tenant'] = self.current_tenant
        node = validated_data.pop('node')
        buyer, supplier = self.get_buyer_supplier(node)
        validated_data['source'] = supplier
        validated_data['destination'] = buyer
        force_create = validated_data.pop('force_create', False)
        validated_data['date'] = validated_data.get(
            'date',timezone.datetime.now().date())
        transactions = transaction_models.ExternalTransaction.objects.filter(
            source=supplier, destination=buyer, price=validated_data['price'],
            destination_quantity=validated_data['quantity'], unit=validated_data['unit'],
            result_batches__product=validated_data['product'],
            date=validated_data['date'],
            upload_timestamp=validated_data.get('upload_timestamp'))
        if transactions.exists() and not force_create:
            # raise base_exceptions.BadRequest(
            #     _("Transaction already created."))
            return transactions.first()
        validated_data = self.prepare_batches(validated_data)
        batch_specific_form = validated_data.pop(
            'batch_specific_form', None)
        internal_form_submission = validated_data.pop(
            'internal_form_submission', None)
        quantity = validated_data.pop('quantity')
        batch_data = validated_data.pop('batch')
        product = validated_data.pop('product')
        if 'batches' in validated_data.keys():
            source_batches = validated_data.pop('batches')
        batch_data['batch'].current_quantity -= batch_data['quantity']
        batch_data['batch'].save()
        validated_data['source_quantity'] = quantity
        validated_data['destination_quantity'] = quantity
        if self.current_tenant.transaction_auto_approval or \
                validated_data['type'] != \
                transaction_consts.ExternalTransactionType.OUTGOING:
            validated_data['status'] = \
                transaction_consts.TransactionStatus.APPROVED
        transaction = \
            transaction_models.ExternalTransaction.objects.create(
                **validated_data)
        batch = batch_data['batch']
        transaction_models.SourceBatch.objects.create(
            transaction=transaction, batch=batch, quantity=quantity,
            creator=current_user, updater=current_user,
            unit=validated_data['unit'])

        if validated_data['type'] != \
                transaction_consts.ExternalTransactionType.INCOMING_WITHOUT_SOURCE:
            supplier_name = supplier.name
        else:
            supplier_name = _("unknown source")

        result_batch = product_models.Batch.objects.create(
            product=product, node=buyer, initial_quantity=quantity,
            current_quantity=quantity, unit=validated_data['unit'],
            creator=current_user, updater=current_user,
            note=validated_data.get('note', ""), tenant=self.current_tenant, 
            batch_specific_form=batch_specific_form, 
            internal_form_submission=internal_form_submission,
            date=validated_data['date'])

        s = _("Batch received from {supplier_name}")  # DO NOT REMOVE. Added to register sentence in translation
        internationalize_attribute(
            obj=result_batch, field_name='name', text='Batch received from {supplier_name}',
            params={
                'supplier_name': supplier_name,
            })
        result_batch.save()

        transaction.result_batches.add(result_batch)
        transaction.save()
        batch_risk_score = (batch.risk_score + buyer.get_risk_score())/2
        if transaction.type == \
                transaction_consts.ExternalTransactionType.REVERSAL:
            self.create_inherited_claims(source_batches, result_batch, transaction)
            batch_risk_score = (batch.risk_score*2) - batch.node.get_risk_score()
        result_batch.risk_score = batch_risk_score
        result_batch.save()
        transaction.notify()
        if validated_data.get('purchase_order', None):
            purchase_order = validated_data['purchase_order']
            self.update_purchase_order(purchase_order, transaction)
        return transaction

    def update(self, instance, validated_data):
        """Update overrided to send notification"""
        instance.approve(note=validated_data.get('note', None))
        if instance.purchase_order:
            self.update_purchase_order(
                instance.purchase_order, instance, user_approve=True)
        data = super().update(instance, validated_data)
        instance.notify()
        return data

    def to_representation(self, instance):
        """
        To representation overrided to return data on the basis of 
        requested node.
        """
        data = super().to_representation(instance)
        if instance.source == self.current_node:
            if instance.type == \
                    transaction_consts.ExternalTransactionType.REVERSAL:
                data['type'] =\
                    transaction_consts.ExternalTransactionType.REVERSAL
            else:
                data['type'] = \
                    transaction_consts.ExternalTransactionType.OUTGOING
            products = instance.source_products()
            data['products'] = ProductBaseSerializer(products, many=True).data
            data['quantity'] = instance.source_quantity
            data['quantity_kg'] = instance.source_quantity_kg
        else:
            if instance.type == \
                transaction_consts.ExternalTransactionType.REVERSAL:
                data['type'] = \
                    transaction_consts.ExternalTransactionType.REVERSAL
            else:
                data['type'] = \
                    transaction_consts.ExternalTransactionType.INCOMING
            products = instance.result_products()
            data['products'] = ProductBaseSerializer(products, many=True).data
            data['quantity'] = instance.destination_quantity
            data['quantity_kg'] = instance.destination_quantity_kg
        return data


class ExternalTransactionListSerializer(serializers.ModelSerializer):
    """
    Seriallizer for external transaction.
    """

    id = custom_fields.IdencodeField(read_only=True)
    creator = custom_fields.IdencodeField(read_only=True)
    transaction_id = serializers.CharField(source='number', read_only=True)
    transaction_id_for_user = serializers.CharField(
        source='number', read_only=True)
    date = serializers.DateField(
        read_only=True, input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'))
    source_products = ProductBaseSerializer(many=True, read_only=True)
    result_products = ProductBaseSerializer(many=True, read_only=True)
    source = custom_fields.IdencodeField(
        serializer=node_serializers.NodeSerializer, 
        related_model=node_models.Node, read_only=True)
    destination = custom_fields.IdencodeField(
        read_only=True, serializer=node_serializers.BasicNodeSerializer)
    unit = custom_fields.IdencodeField(
        read_only=True, serializer=UnitSerializer)
    currency = custom_fields.IdencodeField(
        read_only=True, serializer=currency_serializer.CurrencySerializer)

    class Meta:
        """
        Meta Info.
        """

        model = transaction_models.ExternalTransaction
        fields = (
            'id', 'transaction_id', 'transaction_id_for_user', 'date', 'type', 'source_products',  
            'result_products', 'destination', 'source', 'status', 'unit', 
            'price', 'currency', 'upload_timestamp', 'creator', 'risk_score',
            'risk_score_level',
            )

    def to_representation(self, instance):
        """
        To representation overrided to return data on the basis of 
        requested node.
        """
        data = super().to_representation(instance)
        node = session.get_current_node()
        if instance.source == session.get_current_node():
            if instance.type == \
                    transaction_consts.ExternalTransactionType.REVERSAL:
                data['type'] =\
                    transaction_consts.ExternalTransactionType.REVERSAL
            else:
                data['type'] = \
                    transaction_consts.ExternalTransactionType.OUTGOING
            products = instance.source_products()
            data['products'] = ProductBaseSerializer(products, many=True).data
            data['quantity'] = instance.source_quantity
            data['quantity_kg'] = instance.source_quantity_kg
        else:
            if instance.type == \
                transaction_consts.ExternalTransactionType.REVERSAL:
                data['type'] = \
                    transaction_consts.ExternalTransactionType.REVERSAL
            else:
                data['type'] = \
                    transaction_consts.ExternalTransactionType.INCOMING
            products = instance.result_products()
            data['products'] = ProductBaseSerializer(products, many=True).data
            data['quantity'] = instance.destination_quantity
            data['quantity_kg'] = instance.destination_quantity_kg
        return data


class ExternalTransactionRejectionSerializer(serializers.ModelSerializer):
    """ Serializer to reject an external transaction """

    id = custom_fields.IdencodeField(read_only=True)
    creator = custom_fields.IdencodeField(read_only=True)

    class Meta:
        """
        Meta Info.
        """

        model = transaction_models.ExternalTransaction
        fields = ('id', 'note', 'rejection_reason', 'creator')

    def validate(self, attrs):
        """Validate the provided data."""
        if not self.instance:
            raise base_exceptions.MethodNotAllowed(
                _("Create transaction not allowed"))
        attrs['batches'] = []
        for result_batch in self.instance.result_batches.all():
            if result_batch.initial_quantity !=\
                    result_batch.current_quantity:
                raise base_exceptions.BadRequest(
                    _("Transaction cannot be rejected"))
            attrs['batches'].append({
                'batch': result_batch.idencode,
                'quantity': result_batch.initial_quantity
            })
        node = session.get_current_node()
        if not self.instance.destination == node:
            raise base_exceptions.BadRequest(
                _("Only destination node can reject transaction."))
        return attrs

    @staticmethod
    def reject_claims(transaction=None):
        """
        Rejects all the non-approved claims attached to the txn.
        """
        note = "Claim rejected due to transaction rejected"
        claims = transaction.batch_claims.exclude(
            status=claim_consts.ClaimStatus.APPROVED)
        for claim in claims:
            claim.reject_claim(note=note)
        return True

    @staticmethod
    def update_purchase_order(transaction=None):
        """
        Updates purchase order quantity becuase of the transaction is rejected.
        """
        if transaction.purchase_order:
            po = transaction.purchase_order
            po.sent_quantity -= transaction.source_quantity
            po.save()
            if po.sent_quantity <= 0:
                po.stautus = transaction_consts.PurchaseOrderStatus.PENDING
            po.save()
        return True

    def copy_claims(self, transaction, reversed_transactions):
        from v1.claims.serializers.batch_claim import AttachBatchClaimSerializer
        claim_data = {
            'transaction': reversed_transactions.idencode,
            'claims': [{'claim': i.claim.idencode} for i in transaction.get_claims()]
        }
        abc = AttachBatchClaimSerializer(data=claim_data)
        abc.is_valid(raise_exception=True)
        abc.save()
        return True

    @django_transaction.atomic
    def update(self, instance, validated_data):
        """
        Changes the status of the transaction and 
        creates reverse transaction to the destination node.
        """
        instance.reject(
            note=validated_data.get('note', None), 
            rejection_reason=validated_data.get('rejection_reason', None))

        transaction_data = {
            'type': transaction_consts.ExternalTransactionType.REVERSAL,
            'node': instance.source.idencode,
            'price': instance.price,
            'currency': instance.currency,
            'product':
                instance.result_batches.first().product.idencode,
            'quantity':
                instance.result_batches.first().initial_quantity,
            'unit': instance.unit,
            'batches': validated_data['batches'],
            'name': _('Sending back to {source}').format(source=instance.source.name),
            'note': validated_data.get('note', ""), 
            'force_create': True, 
            'batch_specific_form': instance.result_batches.first().batch_specific_form
        }

        ext_serializer = ExternalTransactionSerializer(
            data=transaction_data, context=self.context
        )
        if not ext_serializer.is_valid():
            raise serializers.ValidationError(ext_serializer.errors)
        ext_trans = ext_serializer.save()
        self.reject_claims(transaction=instance)
        self.copy_claims(transaction=instance, reversed_transactions=ext_trans)
        self.update_purchase_order(transaction=instance)
        instance.notify()
        return instance

    def to_representation(self, instance):
        """Return success message."""
        return {
            'status': True,
            'message': _('Transaction rejected and reversed')}
