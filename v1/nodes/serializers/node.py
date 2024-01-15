from rest_framework import serializers

from django.db import transaction as django_transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from common.drf_custom import fields as custom_fields

from base import session
from base import exceptions
from utilities.functions import decode

from v1.supply_chains import models as supply_models
from v1.supply_chains.serializers import supply_chain as supply_serializers

from v1.accounts.serializers import user as user_serializers
from v1.accounts import models as user_models
from v1.accounts import constants as user_constants

from v1.nodes import models as node_models
from v1.nodes import constants as node_consts

from v1.tenants import models as tenant_models
from v1.tenants.serializers import country as country_serializer
from v1.tenants.serializers import category as category_serializer
from v1.tenants.serializers import tenant as tenant_serializer

from v1.transactions import models as trans_models

from v1.claims import models as claim_models

from v1.dynamic_forms.models import FormSubmission, FormFieldValue

from v1.risk.serializers import score as risk_score_serializers

from v1.supply_chains import models as sc_models
from v1.supply_chains.serializers import supply_chain as sc_serializers


class NodeConnectionSerializer(serializers.ModelSerializer):
    """
    Serializer to list basic node information along with connection status.

    This serializer in used in connection list API to list basic details of
    the node along with the connection status.

    """

    id = custom_fields.IdencodeField(read_only=True)
    number = serializers.IntegerField(read_only=True)
    contact_name = serializers.CharField(required=True)
    connection_status = serializers.IntegerField(read_only=True)
    connection_id = custom_fields.IdencodeField(read_only=True)
    overall_risk_level = serializers.IntegerField(read_only=True)
    rank = serializers.IntegerField()
    products = serializers.SerializerMethodField()
    country = serializers.CharField(source='country.name', read_only=True)
    country_id = serializers.CharField(source='country.idencode', read_only=True)
    province = serializers.CharField(source='province.name', read_only=True)
    province_id = serializers.CharField(source='province.idencode', read_only=True)
    phone = custom_fields.PhoneNumberField(
        required=False, allow_blank=True, allow_null=True)
    operation = custom_fields.IdencodeField(read_only=True)
    sc_risk_level = serializers.SerializerMethodField()

    class Meta:
        """ Meta data """
        model = node_models.Node
        fields = (
            'id', 'number', 'name', 'contact_name', 'email', 'status', 'type',
            'connection_id', 'connection_status', 'upload_timestamp', 'image',
            'overall_risk_level', 'rank', 'country', 'products', 'country_id',
            'province', 'province_id', 'city', 'street', 'registration_no', 'phone',
            'operation', 'sc_risk_level',)
        
    def get_products(self, obj):
        """
        Return unique products names under the txns between the nodes.
        """
        current_node = session.get_current_node()
        sc = self.context['request'].query_params.get(
                'supply_chain', None)
        txns = trans_models.ExternalTransaction.objects.filter(
            Q(source=current_node, destination=obj) | Q(
            source=obj, destination=current_node)
            ).order_by('result_batches__product__name'
            ).distinct('result_batches__product__name')
        if sc:
            sc = supply_models.SupplyChain.objects.get(id=decode(sc))
            txns = txns.filter(result_batches__product__supply_chain=sc)
        products = txns.values_list('result_batches__product__name', flat=True)
        return products
    
    def get_sc_risk_level(self,obj):
        """
        Return supply chain risk level.
        """
        try:
            sc = decode(self.context['request'].query_params.get(
                'supply_chain', None))
        except:
            sc = supply_models.Connection.objects.get(
                id=obj.connection_id).supply_chain.id
        node_sc = obj.supply_chains.filter(
                supply_chain__id=sc).first()
        return node_sc.sc_risk_level


class BasicNodeSerializer(serializers.ModelSerializer):
    """
    """

    id = custom_fields.IdencodeField(read_only=True)
    bc_address = serializers.SerializerMethodField()
    operation = supply_serializers.OperationSerializer()

    def get_bc_address(self, obj):
        """
        """
        return "Block chain is not linked."

    class Meta:
        """ Meta data """
        model = node_models.Node
        fields = (
            "id", "name", "image", "phone",  "bc_address", "operation"
            )


class NodeSerializer(serializers.ModelSerializer):
    """
    """

    id = custom_fields.IdencodeField(read_only=True)
    phone = custom_fields.PhoneNumberField(
        required=False, allow_blank=True, allow_null=True)
    date_invited = serializers.DateTimeField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    operation = custom_fields.IdencodeField(
        related_model=supply_models.Operation, required=False, 
        serializer=supply_serializers.OperationSerializer)
    tenant = custom_fields.IdencodeField(
        required=False, related_model=tenant_models.Tenant)
    members = custom_fields.ManyToManyIdencodeField(
        related_model=user_models.CustomUser, required=False)
    country = custom_fields.IdencodeField(
        serializer=country_serializer.BaseCountrySerializer, 
        related_model=tenant_models.Country, read_only=True)
    province = custom_fields.IdencodeField(
        serializer=country_serializer.ProvinceSerializer, 
        related_model=tenant_models.Province, required=False)
    submission_form = custom_fields.IdencodeField( 
        related_model=FormSubmission, required=False, allow_null=True)
    submission_form_mongo_id = serializers.CharField(required=False)
    incharge = custom_fields.IdencodeField(
        required=False, related_model=user_models.CustomUser, allow_null=True)
    invited_by = custom_fields.IdencodeField(
        related_model=node_models.Node)
    profile_completion = serializers.FloatField(read_only=True)
    can_edit = serializers.BooleanField(read_only=True, source='can_be_edited_by')
    risk_score = custom_fields.IdencodeField(
        serializer=risk_score_serializers.RiskScoreSerializer, read_only=True)
    env_data = custom_fields.IdencodeField( 
        related_model=FormSubmission, required=False, allow_null=True)
    soc_data = custom_fields.IdencodeField( 
        related_model=FormSubmission, required=False, allow_null=True)
    gov_data = custom_fields.IdencodeField( 
        related_model=FormSubmission, required=False, allow_null=True)
    env_data_mongo_id = serializers.CharField(required=False)
    soc_data_mongo_id = serializers.CharField(required=False)
    gov_data_mongo_id = serializers.CharField(required=False)
    company_url = serializers.URLField(
        required=False, allow_blank=True)

    class Meta:
        """ Meta data """
        model = node_models.Node
        exclude = (
            'updater', 'creator', 'updated_on', 'created_on', 'connections',
            )

    def create(self, validated_data):
        validated_data['invited_by'] = validated_data.get('invited_by', session.get_current_node())
        return super(NodeSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.pop('connect_id', None) != instance.connect_id:
            instance.refresh_connect_id()
        instance = super(NodeSerializer, self).update(instance, validated_data)
        if instance.members.count() == 1:
            member = instance.members.first()
            if not member.password:
                from v1.accounts.serializers.user import UserSerializer
                UserSerializer.create_update_user(
                    instance=instance.members.first(), validated_data=validated_data)
                instance.target_connections.order_by('created_on').first().send_invite()
        if instance.tenant.risk_analysis:
            from v1.risk import models as risk_models
            risk_models.RiskScore.update_node_score(instance)
        return instance


class NodeDocumentBaseSerializer(serializers.ModelSerializer):
    """
    """
    id = custom_fields.IdencodeField(read_only=True)
    category = custom_fields.IdencodeField(
        serializer=category_serializer.CategorySerializer, 
        related_model=tenant_models.Category, required=False)

    # extra data about logged-in user's previleges over the node-member.
    extra_info = serializers.SerializerMethodField()
    expiry_date = serializers.DateField(
        required=False, 
        input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'),
        format='%d-%m-%Y')
    created_on = serializers.DateTimeField(
        read_only=True,format='%d-%m-%Y')
    description = serializers.CharField(
        required=False,allow_blank=True)

    class Meta:
        """
        """
        fields = (
            'id', 'name', 'file', 'category','extra_info','expiry_date',
            'file_size','created_on','description',)
        model = node_models.NodeDocument

    def get_extra_info(self, obj):
        """
        Return the logged-in user can change the data of the node-member.
        """
        trnx_comments = trans_models.TransactionComment.objects.filter(
            company_document=obj)
        claim_comment = claim_models.AttachedClaimComment.objects.filter(
            company_document=obj
        )
        form_field_value = FormFieldValue.objects.filter(
            company_document=obj)
        current_user = session.get_current_user()
        node = session.get_current_node()
        types = [
            node_consts.NodeMemberType.ADMIN, 
            node_consts.NodeMemberType.SUPER_ADMIN
            ]
        member = current_user.member_nodes.filter(
            type__in=types, node=node)
        data = {
            "can_edit": False, 
            "can_remove": False
        }
        if obj.creator == current_user:
            data['can_edit'] = True
        if member.exists():
            data['can_edit'] = True
            data['can_remove'] = True
            if trnx_comments or claim_comment or form_field_value:
                data['can_remove'] = False
        return data
    

class NodeDocumentSerializer(NodeDocumentBaseSerializer):
    """
    """
    description = serializers.CharField(
        required=False,allow_blank=True)
    tags = custom_fields.ManyToManyIdencodeField(
        related_model=tenant_models.Tag, required=False,
        serializer=tenant_serializer.TagSerializer)
    folder = custom_fields.IdencodeField(
        required=False,related_model=node_models.Folder,
        write_only=True)

    class Meta:
        """
        """
        fields = NodeDocumentBaseSerializer.Meta.fields + (
            'description', 'tags', 'folder')
        model = node_models.NodeDocument

    def validate(self, attrs):
        """
        Checks same named docs already exists or not.
        """
        if attrs.get('name',None):
            docs = node_models.NodeDocument.objects.filter(
                node=session.get_current_node(),
                name=attrs['name'],is_deleted=False)
            if docs.exists():
                raise exceptions.BadRequest(_(
                    "Document already exists with the same name"))
        return super().validate(attrs)

    def create(self, validated_data):
        """
        """
        validated_data['node'] = session.get_current_node()
        document = super(NodeDocumentSerializer, self).create(
            validated_data)
        document.notify()
        return document
    

class BasicNodeDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer with basic data of the node documents.
    """
    id = custom_fields.IdencodeField(read_only=True)

    class Meta:
        """
        Meta Info.
        """
        model = node_models.NodeDocument
        fields = ('id','name','file')
        read_only_fields = ('id','name','file')


class NodeMemberSerializer(serializers.ModelSerializer):
    """
    """
    id = custom_fields.IdencodeField(read_only=True)
    user_id = custom_fields.IdencodeField(source='user.id', read_only=True)
    name = serializers.CharField(source='user.name')
    email = serializers.CharField(source='user.email')
    image = serializers.ImageField(source='user.image', read_only=True)
    status = serializers.IntegerField(source='user.status', read_only=True)
    default_supply_chain = custom_fields.IdencodeField(
        required=False, related_model=supply_models.SupplyChain)

    # extra data about logged-in user's previleges over the node-member.
    extra_info = serializers.SerializerMethodField()

    class Meta:
        """"""
        model = node_models.NodeMember
        fields = (
            'id', 'user_id', 'name', 'type', 'image', 'email', 'status', 
            'extra_info', 'default_supply_chain')

    def get_extra_info(self, obj):
        """
        Return the logged-in user can change the data of the node-member.
        """
        current_user = session.get_current_user()

        current_user_is_admin = obj.node.node_members.filter(
            user=current_user, type=node_consts.NodeMemberType.SUPER_ADMIN
        ).exists()

        data = {
            "can_edit": False, 
            "can_remove": False
        }
        if obj.user != current_user and current_user_is_admin:
            data['can_edit'] = True
            data['can_remove'] = True
        return data

    @staticmethod
    def create_user(validated_data):
        """
        Creates user account for Node incharge
        """
        from v1.accounts.serializers.user import UserSerializer
        return UserSerializer.create_update_user(validated_data=validated_data)

    def create(self, validated_data):
        """
        """
        validated_data['node'] = session.get_current_node()
        validated_data['tenant'] = validated_data['node'].tenant
        validated_data.update(**validated_data['user'])
        user = self.create_user(validated_data)
        validated_data['user'] = user
        member_data = node_models.NodeMember.clean_dict(validated_data)

        member = super().create(member_data)
        member.send_invite()
        return member
    
    @django_transaction.atomic
    def update(self, instance, validated_data):
        """Update overrided to change updater and notify the user."""
        if 'type' in validated_data.keys() and \
            validated_data['type'] != instance.type:
            instance.user.make_force_logout()
        member = super().update(instance, validated_data)
        return member


class BasicNodeSerializer(serializers.ModelSerializer):
    """
    Basic node serializer for node search with ro-ai.
    """
    id = custom_fields.IdencodeField(read_only=True)
    country = custom_fields.IdencodeField(
        serializer=country_serializer.BaseCountrySerializer, 
        related_model=tenant_models.Country, read_only=True)
    province = custom_fields.IdencodeField(
        serializer=country_serializer.BaseProvinceSerializer, 
        related_model=tenant_models.Province, read_only=True)
    name = serializers.CharField(read_only=True)

    class Meta:
        """
        Meta info.
        """
        model = node_models.Node
        fields = ('id', 'name', 'country', 'province')
