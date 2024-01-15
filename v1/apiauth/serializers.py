"""
Serializer customization for Authentication
"""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import \
    TokenRefreshSerializer as SJWTTokenRefreshSerializer
from rest_framework_simplejwt.state import token_backend
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation

import utilities.functions
from base import exceptions
from base import session
from base import response
from common.drf_custom import fields
from utilities.functions import decode

from v1.accounts.models import CustomUser, ValidationToken, PrivacyPolicy
from v1.accounts import constants as acc_constants

from v1.tenants.models import Tenant
from v1.nodes.models import Node
from v1.nodes.models import NodeMember
from v1.tenants import serializers as tenant_sreializers


class APILoginSerializer(TokenObtainPairSerializer):
    """
    Serializer to validate and return token after logging in the user.
    """

    tenant = fields.IdencodeField(related_model=Tenant)
    node: Node = None
    tenant_object: Tenant = None
    node_member: NodeMember = None

    def validate(self, attrs):
        """
        Along with the inherited auth token and refresh token, id of
        user, node and tenant are added into the response.
        """
        self.tenant_object = attrs['tenant']
        data = super().validate(attrs)
        data['user_id'] = self.user.idencode
        data['node_id'] = self.node.idencode
        data['tenant_id'] = self.tenant_object.idencode
        data['user_status'] = self.user.status
        self.user.set_active()
        return data

    def get_token(self, user):
        if not self.tenant_object.node_members.filter(user=user).exists():
            raise exceptions.AuthenticationFailed(_("User does not have access to Tenant"))
        self.node = user.get_default_node()
        if not self.node:
            raise exceptions.AuthenticationFailed(_("User does not have access any Nodes"))
        try:
            node_member = NodeMember.objects.get(
                node=self.node, user=user, is_active=True)
        except NodeMember.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                _("Invalid Node or User does not have access."), 'invalid_node'
            )
        token = super().get_token(user)
        user.disable_force_logout()
        self.node.activate_connections()
        token['session_data'] = {
            'user_id': user.idencode,
            'tenant_id': self.tenant_object.idencode,
            'node_id': self.node.idencode,
            'member_type': node_member.type
        }
        return token


class TokenRefreshSerializer(SJWTTokenRefreshSerializer):
    """
    API to refresh token along with node change.
    """
    node = fields.IdencodeField(related_model=Node)

    def validate(self, attrs):
        super(TokenRefreshSerializer, self).validate(attrs)
        node = attrs['node']
        token_payload = token_backend.decode(attrs['refresh'])
        session_data = token_payload['session_data']
        try:
            user = get_user_model().objects.get(
                pk=decode(session_data['user_id']), 
                status=acc_constants.UserStatus.ACTIVE, 
                force_logout=False)
        except get_user_model().DoesNotExist:
            raise exceptions.AuthenticationFailed(
                _("No active account found with the given credentials"),
                'no_active_account'
            )
        try:
            tenant = Tenant.objects.filter(
                pk=decode(session_data['tenant_id']), node_members__user=user
            ).order_by('id').distinct('id').get()
        except Tenant.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                _("Invalid tenant or User does not have access."),
                'invalid_tenant'
            )

        try:
            node_member = NodeMember.objects.get(
                node=node, user=user, is_active=True)
        except NodeMember.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                _("Invalid Node or User does not have access."), 'invalid_node'
            )
        refresh = RefreshToken(attrs['refresh'])
        refresh['session_data']['node_id'] = node.idencode
        attrs['refresh'] = str(refresh)
        data = super().validate(attrs)
        user.set_default_node(node)
        node.activate_connections()
        data['user_id'] = user.idencode
        data['node_id'] = node.idencode
        data['tenant_id'] = tenant.idencode
        data['member_type'] = node_member.type
        data['policy_accepted'] = user.policy_accepted
        data['current_policy'] = \
            PrivacyPolicy.current_privacy_policy().idencode
        return data


class APIPasswordResetSerializer(serializers.Serializer):
    """
    Serializer to send email for user password reset
    """
    email = serializers.EmailField()
    tenant = fields.IdencodeField()

    def create(self, validated_data):
        session.set_to_local('tenant_id', validated_data['tenant'])

        try:
            ip, location, device = utilities.functions.client_details((self.context['request']))
            user = CustomUser.objects.get(email=validated_data['email'], is_active=True)
            user.reset_password(ip, location, device)
        except CustomUser.DoesNotExist:
            raise exceptions.BadRequest(
                _("Email is not registered with any user"))
        return validated_data

    def to_representation(self, instance):
        return {}


class ValidationSerializer(serializers.Serializer):
    """
    Serializer to send email for user password reset
    """
    validation_token = serializers.CharField(required=False)
    user = fields.IdencodeField(related_model=CustomUser, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False)
    node = fields.IdencodeField(
        related_model=Node, required=False, allow_null=True)

    def validate_validation_token(self, value):
        token_validation = {
                'valid': True,
                'value': value,
                'message': "",
                'set_password': False,
            }
        try:
            validation_token = ValidationToken.objects.get(key=value)

            token_validation['object'] = validation_token
            if not validation_token.is_valid():
                token_validation['valid'] = False
                token_validation['message'] = _("Invalid validation token")
                # raise serializers.ValidationError(_("Invalid validation token"))
        except ValidationToken.DoesNotExist:
            token_validation['valid'] = False
            token_validation['message'] = _("Invalid validation token")
            # raise serializers.ValidationError(_("Invalid validation token"))
        return token_validation

    def validate_email(self, value):
        email_validation = {
                'valid': True,
                'value': value,
                'message': "",
            }
        if CustomUser.objects.filter(email=value).exists():
            email_validation['valid'] = False
            email_validation['message'] = _("Email already taken.")
        return email_validation

    def validate_password(self, value):
        password_validate = {
                'valid': True,
                'value': value,
                'message': "",
            }
        try:
            password_validation.validate_password(value)
        except Exception as e:
            password_validate['valid'] = False
            password_validate['message'] = str(e)
        return password_validate

    def validate(self, attrs):
        user = attrs.get('user', None)
        attrs['user'] = user.id
        node = attrs.pop('node', None)
        validation_token = attrs.get('validation_token', {'object': None}).pop('object')
        if node and not node.node_members.filter(user=user).exists():
            raise serializers.ValidationError(
                _("Member is removed or not available, please contact admin."))
        if validation_token:
            if not user:
                raise serializers.ValidationError(
                    {'validation_token': [_("User ID is required to validate Validation Token")]})
            if not user.password or not user.has_usable_password() or \
                    validation_token.type == acc_constants.ValidationTokenType.RESET_PASS:
                attrs['validation_token']['set_password'] = True
            if user != getattr(validation_token, 'user', None):
                attrs['validation_token']['value'] = "-"
                attrs['validation_token']['valid'] = False
                attrs['validation_token']['message'] = _("Invalid validation token")
        return attrs

    def create(self, validated_data):
        return validated_data

    def to_representation(self, instance):
        return instance


class PasswordResetConfirmSerializer(ValidationSerializer):
    """
    Serializer to change password of user
    """
    token = serializers.CharField()
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    old_password = serializers.CharField(max_length=128, required=False)

    def validate(self, attrs):
        attrs = super(PasswordResetConfirmSerializer, self).validate(attrs)
        try:
            attrs['token'] = ValidationToken.objects.get(key=attrs['token'])
        except:
            raise exceptions.BadRequest(_("Token does not exist."))
        try:
            attrs['user'] = CustomUser.objects.get(id=attrs['user'])
        except:
            raise exceptions.BadRequest(_("User does not exist"))
        if attrs['user'].password and attrs['user'].has_usable_password() and \
                attrs['token'].type != acc_constants.ValidationTokenType.RESET_PASS:
            raise serializers.ValidationError(
                _("Password already set. User reset password to change password."))
        if attrs.get('old_password', None) and \
            not attrs['user'].check_password(attrs['old_password']):
            raise serializers.ValidationError(_("Password is incorrect."))
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError(_("Your passwords didn't match."))
        return attrs

    def create(self, validated_data):
        super(PasswordResetConfirmSerializer, self).create(validated_data)
        user = validated_data['user']
        user.set_password(validated_data['new_password1'])
        if validated_data['token'].type == \
            acc_constants.ValidationTokenType.INVITE:
            user.accepted_policy = PrivacyPolicy.current_privacy_policy()
        user.save()
        validated_data['token'].invalidate()
        return validated_data

    def to_representation(self, instance):
        return {}


class CheckPasswordSerializer(serializers.Serializer):
    """Serializer to check user password is correct."""

    password = serializers.CharField()

    def create(self, validated_data):
        """Create overrided to check the password is correct."""
        user = session.get_current_user()
        if not user.check_password(validated_data['password']):
            raise exceptions.NoValueResponse(_("Password is incorrect"))
        return validated_data

    def to_representation(self, instance):
        """Return success response"""
        return {"message": "Password is correct"}

class UserTenantSerializer(serializers.Serializer):
    """Serializer to list user's tenant - if user authenticates"""
    email = serializers.CharField()
    password =serializers.CharField()

    def create(self, validated_data):
        """Create overriden to check the email and password"""
        user = get_user_model().objects.filter(username=validated_data['email']).first()
        if not user:
            raise exceptions.AuthenticationFailed(_("email or password is incorrect"))
        
        if not user.check_password(validated_data['password']):
            raise exceptions.AuthenticationFailed(_("email or password is incorrect"))
        
        validated_data['user'] = user
        
        return validated_data
