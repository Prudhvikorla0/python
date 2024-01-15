"""
Serializers for connections
"""

from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from base import session
from common.drf_custom import fields
from base import exceptions

from v1.risk import models as risk_models

from v1.accounts.models import CustomUser

from v1.nodes.models import Node
from v1.nodes.models import NodeMember
from v1.nodes import constants as node_constants
from v1.nodes.serializers import node as node_serializers

from v1.tenants import models as tenant_models
from v1.tenants.serializers import tenant as tenant_serializer

from v1.supply_chains import models as sc_models
from v1.supply_chains.serializers import supply_chain as sc_serializers
from v1.supply_chains import constants as sc_constants

from v1.dynamic_forms import models as dynamic_models


class ConnectExistingNodeSerializer(serializers.ModelSerializer):
    """
    Serializer to add a connection to an existing node for a supply chain.
    """
    id = fields.IdencodeField(read_only=True)
    source = fields.IdencodeField(read_only=True)
    target = fields.IdencodeField(read_only=True)
    node = fields.IdencodeField(
        related_model=Node, source='target', write_only=True)
    supply_chain = fields.IdencodeField(
        related_model=sc_models.SupplyChain)
    tags = fields.ManyToManyIdencodeField(
        related_model=tenant_models.Tag, required=False)
    submission_form = fields.IdencodeField(
        related_model=dynamic_models.FormSubmission, required=False)
    submission_form_mongo_id = serializers.CharField(required=False)

    class Meta:
        model = sc_models.Connection
        exclude = (
            'tenant', 'graph_id', 'status', 'creator', 'updater', 
            'updated_on', 'created_on'
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

        self.should_create_node = True
        if 'data' in kwargs and 'node' in kwargs['data'] and kwargs['data']['node']:
            self.should_create_node = False
            self.fields['operation'].required = False
            self.fields['province'].required = False
        super(ConnectExistingNodeSerializer, self).__init__(instance, data, **kwargs)

    @staticmethod
    def create_connection(validated_data):
        """
        Creates connection between source and target in that supply chain
        """
        tags = validated_data.pop('tags', [])
        connection_data = sc_models.Connection.clean_dict(validated_data)
        connection, created = sc_models.Connection.objects.get_or_create(
            **connection_data)
        connection.tags.add(*tags)
        if connection_data['source'].tenant.symmetrical_connection:
            connection.is_buyer = True
            connection.is_supplier = True
            connection.save()
            connection_data['is_buyer'] = True
            connection_data['is_supplier'] = True
        else:
            is_buyer = validated_data.get('is_buyer',False)
            is_supplier = validated_data.get('is_supplier',True)
            connection.is_buyer = is_buyer
            connection.is_supplier = is_supplier
            connection.save()
            if not (is_buyer and is_supplier):
                connection_data['is_buyer'] = not is_buyer
                connection_data['is_supplier'] = not is_supplier
        connection_data['source'], connection_data['target'] = \
            connection_data['target'], connection_data['source']
        connection_data['submission_form'] = connection.submission_form
        connection_data['connection_pair'] = connection
        connection_data['initiation'] = sc_constants.ConnectionInitiation.SYSTEM
        pair_connection, created = sc_models.Connection.objects.get_or_create(
            **connection_data)
        connection.connection_pair = pair_connection
        connection.save()
        return connection

    @atomic
    def create(self, validated_data):
        """
        Over-ridden to update tenant and source before creating connection
        """
        validated_data['tenant'] = self.current_tenant
        validated_data['source'] = self.current_node
        connection = self.create_connection(validated_data)
        return connection


class ConnectNodeSerializer(ConnectExistingNodeSerializer):
    """
    Serializer to add a connection to a new node for a supply chain
    """
    number = serializers.IntegerField(read_only=True)
    node = fields.IdencodeField(
        related_model=Node, source='target', required=False, write_only=True)
    operation = fields.IdencodeField(related_model=sc_models.Operation)
    province = fields.IdencodeField(related_model=tenant_models.Province)
    phone = fields.PhoneNumberField(
        required=False, allow_blank=True, allow_null=True)
    submission_form = fields.IdencodeField(
        related_model=dynamic_models.FormSubmission, required=False, 
        allow_null=True)
    submission_form_mongo_id = serializers.CharField(required=False)
    image = fields.RemovableImageField(
        required=False, allow_blank=True, allow_null=True)
    is_buyer = serializers.BooleanField(required=False)
    is_supplier = serializers.BooleanField(required=False)

    class Meta:
        model = Node
        exclude = (
            'updater', 'creator', 'updated_on', 'created_on',
            'tenant', 'latitude', 'longitude', 'zipcode',
            'description', 'invited_on', 'joined_on', 'status', 'is_verified',
            'is_producer', 'is_verifier', 'incharge'
        )

    def __init__(self, *args, **kwargs):
        super(ConnectNodeSerializer, self).__init__(*args, **kwargs)
        self.should_create_node = True
        if 'data' in kwargs and 'node' in kwargs['data'] and kwargs['data']['node']:
            self.should_create_node = False
            self.fields['operation'].required = False
            self.fields['province'].required = False

    @staticmethod
    def create_node(validated_data):
        """
        Creates node
        """
        nodes = Node.objects.filter(
                tenant=validated_data['tenant'],
                operation=validated_data.get('operation', None),
                name=validated_data.get('name', None),
                province=validated_data.get('province', None)
        )
        if validated_data.get('upload_timestamp', None):
            # Duplication check
            nodes =nodes.filter(
                upload_timestamp=validated_data.get('upload_timestamp', None),
            )

        if nodes:
            return nodes.first()

        node_data = Node.clean_dict(validated_data)
        province = node_data.get('province', None)
        if province:
            node_data['country'] = province.country
            node_data['latitude'] = province.latitude
            node_data['longitude'] = province.longitude
        node_serializer = node_serializers.NodeSerializer(data=node_data)
        if not node_serializer.is_valid():
            raise serializers.ValidationError(node_serializer.errors)
        node = node_serializer.save()
        if validated_data['tenant'].risk_analysis:
            risk_models.RiskScore.update_node_score(node)
        return node

    @staticmethod
    def create_user(validated_data):
        """
        Creates user account for Node incharge
        """
        from v1.accounts.serializers.user import UserSerializer
        return UserSerializer.create_update_user(validated_data=validated_data)

    @staticmethod
    def create_member(validated_data):
        """
        Creates team member for node
        """
        member_data = NodeMember.clean_dict(validated_data)
        member_data['type'] = node_constants.NodeMemberType.SUPER_ADMIN
        member,__ = NodeMember.objects.update_or_create(
            tenant=member_data['tenant'], 
            user=validated_data['user'],
            node=validated_data['node'],
            defaults=member_data
        )
        return member

    @staticmethod
    def create_node_supplychain(node, supply_chain):
        """
        Method create suppplychain under the target node.
        If the supplychain is new to the node.
        """
        sc, created = sc_models.NodeSupplyChain.objects.get_or_create(
            supply_chain=supply_chain, node=node)
        if sc and not sc.is_active:
            sc.is_active = True
        if created:
            node_score = node.get_risk_score()
            sc_score = 0
            if node.type == node_constants.NodeType.PRODUCER:
                sc_score = 100
            sc.sc_risk_score = (node_score + sc_score)/2
        sc.save()
        return True

    @atomic
    def create(self, validated_data):
        """
        Creates user, node and node member before calling parent class to
        create connection
        """
        validated_data['tenant'] = self.current_tenant
        validated_data['source'] = self.current_node
        validated_data['invited_by'] = self.current_node
        if self.should_create_node:
            user = self.create_user(validated_data)
            validated_data['incharge'] = user
            node = self.create_node(validated_data)
            validated_data['node'] = node
            old_connection = sc_models.Connection.objects.filter(
                source=self.current_node,target=node,
                supply_chain=validated_data['supply_chain'])
            if old_connection.exists():
                raise exceptions.BadRequest(_("Connection already exists"))
            if user:
                validated_data['user'] = user
                validated_data['member'] = self.create_member(validated_data)
                user.set_default_node(node)
            validated_data['target'] = node
        if validated_data['tenant'].connection_auto_approval:
            validated_data['status'] = sc_constants.ConnectionStatus.APPROVED
        connection = super(ConnectNodeSerializer, self).create(validated_data)
        self.create_node_supplychain(
            validated_data['target'], validated_data['supply_chain'])
        connection.send_invite()
        # connection.update_graphdb()
        return connection

    def to_representation(self, instance):
        """
        Over-ridden to return connection information instead of Node info.
        """
        return ConnectExistingNodeSerializer(instance).data


class ConnectionSerializer(serializers.ModelSerializer):
    """
    Serializer to get details of connection.
    """
    id = fields.IdencodeField(read_only=True)
    target = fields.IdencodeField(
        serializer=node_serializers.NodeSerializer, read_only=True)
    supply_chain = fields.IdencodeField(
        serializer=sc_serializers.SupplyChainSerializer, read_only=True)
    tags = fields.ManyToManyIdencodeField(
        serializer=tenant_serializer.TagSerializer, 
        related_model=tenant_models.Tag, 
        required=False)
    submission_form = fields.IdencodeField(read_only=True)
    status = fields.serializers.IntegerField()
    is_supplier = serializers.BooleanField(required=False)
    is_buyer = serializers.BooleanField(required=False)

    class Meta:
        model = sc_models.Connection
        fields = (
            'id', 'target', 'supply_chain', 'tags', 'submission_form', 'status', 
            'is_supplier', 'is_buyer', 'sc_risk_score', 'sc_risk_level')

    @atomic
    def update(self, instance, validated_data):
        if 'status' in validated_data:
            pair = instance.connection_pair
            if pair:
                pair.status = validated_data['status']
                pair.save()
        return super(ConnectionSerializer, self).update(instance, validated_data)
