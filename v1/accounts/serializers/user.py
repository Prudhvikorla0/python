"""Serializers related to user are stored here."""
from rest_framework import serializers

from common.drf_custom import fields as custom_fields
from base import session
from base import exceptions as custom_exceptions

from v1.accounts import models as user_models
from v1.accounts.serializers.other_apps import UserNodeSerializer

from v1.nodes import models as node_models

from v1.tenants import models as tenant_models

from v1.supply_chains import models as sc_models


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user."""

    id = custom_fields.IdencodeField(read_only=True)
    managing_nodes = custom_fields.ManyToManyIdencodeField(
        read_only=True, 
        serializer=UserNodeSerializer, 
        source='node_members', related_model='v1.nodes.NodeMember')
    tenant = custom_fields.IdencodeField(
        required=False, related_model=tenant_models.Tenant)
    default_node = custom_fields.IdencodeField(
        read_only=True, related_model=node_models.Node)
    default_supply_chain = custom_fields.IdencodeField(
        required=False, related_model=sc_models.SupplyChain)
    phone = custom_fields.PhoneNumberField(
        required=False, allow_blank=True, allow_null=True)
    accepted_policy = custom_fields.IdencodeField(
        required=False, related_model=user_models.PrivacyPolicy)
    current_policy = serializers.SerializerMethodField()
    language = serializers.CharField(required=False)
    walkthrough_status = serializers.DictField(required=False)

    class Meta:
        """Meta info."""

        model = user_models.CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'dob', 'phone',
                  'address', 'image', 'updated_email', 'managing_nodes', 
                  'default_node', 'tenant', 'default_supply_chain', 
                  'accepted_policy', 'policy_accepted', 'current_policy', 
                  'user_config', 'language','walkthrough_status',]

    def get_current_policy(self, obj):
        """Return current policy"""
        return user_models.PrivacyPolicy.current_privacy_policy().idencode

    @staticmethod
    def create_update_user(validated_data, instance=None):
        """
        Creates user account for Node incharge
        """
        if not instance:
            if validated_data.get('email', None):
                matching_users = user_models.CustomUser.objects.filter(email=validated_data['email'])
                if matching_users.exists():
                    return matching_users.first()
            elif validated_data.get('phone', None):
                matching_users = user_models.CustomUser.objects.filter(phone=validated_data['phone'])
                if matching_users.exists():
                    return matching_users.first()
            else:
                return None
        validated_data['contact_name'] = validated_data.get(
            'contact_name', None) or validated_data.get('name', " ")
        user_data = user_models.CustomUser.clean_dict(validated_data)
        if 'email' in  user_data.keys() and not user_data['email']:
            user_data.pop('email')
        name = validated_data['contact_name'].strip().split(' ')
        user_data['first_name'], user_data['last_name'] = name[0], ' '.join(name[1:])
        user_serializer = UserSerializer(instance=instance, data=user_data, partial=True)
        if not user_serializer.is_valid():
            raise serializers.ValidationError(user_serializer.errors)
        return user_serializer.save()
    
    def update(self, instance, validated_data):
        """
        Update Overrided to update default supplychain of a node  of the 
        """
        default_supply_chain = validated_data.pop('default_supply_chain',None)
        if default_supply_chain:
            node = session.get_current_node()
            try:
                node_member = instance.member_nodes.get(node=node)
            except:
                raise custom_exceptions.NotFound("Node member doesn't exists")
            node_member.default_supply_chain = default_supply_chain
            node_member.save()
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        """
        To representation added to update default sc in response.
        """
        data = super().to_representation(instance)
        data['default_supply_chain'] = instance.get_default_sc().idencode
        return data


class BasicUserSerializer(serializers.ModelSerializer):

    id = custom_fields.IdencodeField(read_only=True)
    tenant = custom_fields.IdencodeField(
        required=False, related_model=tenant_models.Tenant)

    class Meta:
        """Meta info."""

        model = user_models.CustomUser
        fields = [
            'id', 'first_name', 'last_name', 'email', 'tenant', 'image'
            ]


class PrivacyPolicySerializer(serializers.ModelSerializer):
    """
    Serializer for Privacy policy.
    """

    id = custom_fields.IdencodeField(read_only=True)
    class Meta:
        """Meta info."""
        model = user_models.PrivacyPolicy
        fields = ['id', 'content', 'version', 'date', 'since']
