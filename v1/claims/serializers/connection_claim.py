"""Serializers related to company claim."""

from django.db import transaction as django_transaction
from django.utils.translation import gettext_lazy as _

from common.drf_custom import fields as custom_fields
from base import exceptions
from base import session

from v1.claims import models as claim_models
from v1.claims import constants as claim_constants
from v1.claims.serializers import claim as claim_serializers

from v1.supply_chains import models as sup_models
from v1.supply_chains.serializers import connections as conn_serializers


class ConnectionCriterionSerializer(claim_serializers.AttachCriterionSerializer):
    """
    Serializer for criterion and submission form.
    """
    connection_claim = custom_fields.IdencodeField(
        related_model=claim_models.ConnectionClaim,
        allow_null=True, required=False)

    class Meta:
        """Meta Info."""
        model = claim_models.ConnectionCriterion
        fields = claim_serializers.AttachCriterionSerializer.Meta.fields + (
            'connection_claim',)


class ConnectionClaimSerializer(claim_serializers.AttachedClaimSerializer):
    """
    Serializer for connection claim.
    """

    connection = custom_fields.IdencodeField(
        related_model=sup_models.Connection, 
        serializer=conn_serializers.ConnectionSerializer, required=False)
    criteria = ConnectionCriterionSerializer(many=True, required=False)

    class Meta:
        """
        Meta Info.
        """

        model = claim_models.ConnectionClaim
        fields = claim_serializers.AttachedClaimSerializer.Meta.fields + (
            'connection', 'criteria')

    def validate(self, attrs):
        """Validate company claim data."""
        if 'claim' not in attrs.keys():
            raise exceptions.BadRequest(_("Claim is required."))
        if 'connection' not in attrs.keys():
            raise exceptions.BadRequest(_("Connection is required."))
        if not attrs['claim'].attach_while_connecting:
            raise exceptions.BadRequest(_("Claim is not attachable while connecting."))
        return super().validate(attrs)

    @django_transaction.atomic
    def create(self, validated_data):
        """
        Create overrided to create nodeclaims and nodeclaimcriterions.
        """
        validated_data['attached_to'] = claim_constants.ClaimAttachedTo.CONNECTION
        validated_data['attached_by'] = session.get_current_node()
        if validated_data['claim'].verification_type == \
                claim_constants.ClaimVerificationMethod.SECOND_PARTY:
            validated_data['verifier'] = session.get_current_node()
        connection_claims = claim_models.ConnectionClaim.objects.filter(
            connection=validated_data['connection'], 
            claim=validated_data['claim']
        ).exclude(status=claim_constants.ClaimStatus.REJECTED)
        if connection_claims.exists():
            return connection_claims.first()
        criteria = validated_data.pop('criteria', None)
        connection_claim = claim_models.ConnectionClaim.objects.create(
            **validated_data)
        if criteria:
            for criterion in criteria:
                criterion['connection_claim'] = connection_claim
                criterion = ConnectionCriterionSerializer(data=criterion)
                if not criterion.is_valid():
                    raise exceptions.BadRequest(
                        _("Connection criterion creation failed."))
                criterion.save()
        if validated_data.get('verifier', None):
            connection_claim.notify_claim_attached()
        return connection_claim
