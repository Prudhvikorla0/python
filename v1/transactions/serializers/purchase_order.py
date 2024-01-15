from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from base import session, exceptions
from common.drf_custom import fields as custom_fields
from v1.accounts.serializers.user import BasicUserSerializer
from v1.claims import models as claim_models
from v1.claims.serializers.claim import ClaimBasicSerializer
from v1.dynamic_forms import models as form_models
from v1.nodes import models as node_model
from v1.nodes.serializers import node as node_serializers
from v1.products import models as product_models
from v1.products.serializers import product as product_serializers
from v1.supply_chains import models as supply_model, constants as sc_constants
from v1.tenants import models as tenant_models
from v1.tenants.serializers import currency as currency_serializers
from v1.transactions import models as txn_models, constants as txn_consts


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and retrieving purchase orders details.
    """

    id = custom_fields.IdencodeField(read_only=True)
    status = serializers.IntegerField(required=False)

    sender = custom_fields.IdencodeField(
        serializer=node_serializers.BasicNodeSerializer, read_only=True)
    receiver = custom_fields.IdencodeField(
        serializer=node_serializers.BasicNodeSerializer, read_only=True)

    supplier = custom_fields.IdencodeField(
        related_model=node_model.Node, source='receiver', write_only=True)

    creator = custom_fields.IdencodeField(
        serializer=BasicUserSerializer, read_only=True)
    updater = custom_fields.IdencodeField(
        serializer=BasicUserSerializer, read_only=True)
    product = custom_fields.IdencodeField(
        related_model=product_models.Product,
        serializer=product_serializers.ProductBaseSerializer)
    currency = custom_fields.IdencodeField(
        related_model=tenant_models.Currency,
        serializer=currency_serializers.CurrencySerializer)
    unit = custom_fields.IdencodeField(
        related_model=product_models.Unit,
        serializer=product_serializers.UnitSerializer)
    date = serializers.DateField(
        input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'))
    expected_date = serializers.DateField(
        input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'))
    quantity = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3)
    sent_quantity = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3, read_only=True)
    remaining_quantity = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3, read_only=True)
    claims = custom_fields.ManyToManyIdencodeField(
        related_model=claim_models.Claim, serializer=ClaimBasicSerializer,
        required=False)
    submission_form = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission, required=False,
        allow_null=True)
    submission_form_mongo_id = serializers.CharField(required=False)

    class Meta:
        model = txn_models.PurchaseOrder
        fields = ('id', 'status', 'sender', 'receiver', 'supplier',
                  'creator', 'updater', 'product', 'currency', 'unit',
                  'price', 'date', 'expected_date', 'quantity',
                  'sent_quantity', 'remaining_quantity', 'claims',
                  'comment', 'submission_form', 'number', 'rejection_note',
                  'extra_info', 'submission_form_mongo_id',)

    def validate(self, attrs):
        if self.instance:
            if not self.instance.is_modifiable():
                raise serializers.ValidationError(
                    _("Purchase order cannot be modified. It might be "
                    "Completed/Rejected."))
        return attrs

    def create(self, validated_data):
        validated_data['sender'] = session.get_current_node()
        try:
            supply_model.Connection.objects.get(
                source=validated_data['sender'],
                target=validated_data['receiver'],
                supply_chain=validated_data['product'].supply_chain,
                status=sc_constants.ConnectionStatus.APPROVED)
        except supply_model.Connection.DoesNotExist:
            raise exceptions.BadRequest(
                _("{sender} not connected to {receiver} in the {sc_name} supplychain.").format(
                    sender=validated_data['sender'],
                    receiver=validated_data['receiver'],
                    sc_name=validated_data['product'].supply_chain.name))
        purchase_order = super(PurchaseOrderSerializer, self).create(
            validated_data)
        purchase_order.notify()
        return purchase_order

    def update(self, instance, validated_data):
        notified = False
        validated_data.pop('receiver', None)
        if instance.status in \
                [txn_consts.PurchaseOrderStatus.APPROVED,
                 txn_consts.PurchaseOrderStatus.REJECTED]:
            raise exceptions.BadRequest(
                _("Order cannot be changed for already "
                "Completed/Rejected order"))
        if instance.status == txn_consts.PurchaseOrderStatus.PARTIAL and \
            validated_data['status'] == txn_consts.PurchaseOrderStatus.PARTIAL:
            raise exceptions.BadRequest(
                _("Order cannot be changed , stock sharing already started."))
        current_node = session.get_current_node()
        if 'status' in validated_data.keys():
            if validated_data['status'] in \
                    [txn_consts.PurchaseOrderStatus.REJECTED, ]:
                if instance.receiver != current_node:
                    raise exceptions.BadRequest(
                        _("Only the receiver can reject the order."))
                instance.reject(validated_data['rejection_note'])
                notified = True
            elif validated_data['status'] in \
                    [txn_consts.PurchaseOrderStatus.CANCELLED, ]:
                if instance.sender != current_node:
                    raise exceptions.BadRequest(
                        _("Only the sender can remove the order."))
                instance.remove()
                notified = True
        if not notified:
            instance.notify(update=True)
        return super().update(instance, validated_data)


class BasicPurchaseOrderSerializer(serializers.ModelSerializer):
    """
    Serializer for PurchaseOrder model. Used as base for orders.
    """

    id = custom_fields.IdencodeField(read_only=True)
    status = serializers.IntegerField(required=False)
    receiver = custom_fields.IdencodeField(
        serializer=node_serializers.BasicNodeSerializer, read_only=True)
    product = custom_fields.IdencodeField(
        related_model=product_models.Product,
        serializer=product_serializers.ProductBaseSerializer)
    expected_date = serializers.DateField(
        input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'))
    quantity = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3)

    class Meta:
        model = txn_models.PurchaseOrder
        fields = ('id', 'number', 'status', 'receiver', 'product',
                  'expected_date', 'quantity')


class DeliveryNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating delivery notification.
    """

    id = custom_fields.IdencodeField(read_only=True)
    purchase_order = custom_fields.IdencodeField(
        related_model=txn_models.PurchaseOrder,
        serializer=BasicPurchaseOrderSerializer)
    expected_date = serializers.DateField(
        required=False, input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'))
    quantity = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3, required=False)

    class Meta:
        model = txn_models.DeliveryNotification
        fields = ('id', 'quantity', 'expected_date', 'comment',
                  'purchase_order')

    def create(self, validated_data):
        ordered_quantity = validated_data['purchase_order'].quantity
        if 'quantity' in validated_data.keys():
            if ordered_quantity < validated_data['quantity']:
                raise serializers.ValidationError(
                    _("Delivering quantity mismatch"))
        delivery_notif = super(DeliveryNotificationSerializer, self).create(
            validated_data)
        delivery_notif.notify()
        return delivery_notif


class BasicDeliveryNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for basic delivery notification.
    """

    id = custom_fields.IdencodeField(read_only=True)
    purchase_order = custom_fields.IdencodeField(
        related_model=txn_models.PurchaseOrder)
    expected_date = serializers.DateField(
        required=False, input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'))
    quantity = custom_fields.RoundingDecimalField(
        max_digits=25, decimal_places=3, required=False)

    class Meta:
        model = txn_models.DeliveryNotification
        fields = ('id', 'quantity', 'expected_date', 'comment',
                  'purchase_order')
