"""Serializers related to company claim."""

from rest_framework import serializers
from django.db import transaction as django_transaction
from django.utils.translation import gettext_lazy as _

from common.drf_custom import fields as custom_fields
from base import exceptions
from base import session

from v1.claims import models as claim_models
from v1.claims import constants as claim_constants
from v1.claims.serializers import claim as claim_serializers

from v1.nodes import models as node_models
from v1.nodes.serializers import node as node_serializers

from v1.dynamic_forms import models as form_models


class NodeCriterionSerializer(serializers.ModelSerializer):
    """
    Serializer for criterion and submission form.
    """

    criterion = custom_fields.IdencodeField(
        related_model=claim_models.Criterion)
    form_submission = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission)
    submission_form_mongo_id = serializers.CharField(required=False)
    status = serializers.IntegerField(required=False)
    node_claim = custom_fields.IdencodeField(
        related_model=claim_models.NodeClaim,
        allow_null=True, required=False)
    form = custom_fields.IdencodeField(
        related_model=form_models.Form, 
        source='form_submission.form', 
        read_only=True, default=None)
    verifier_submission = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission, read_only=True)
    verifier_form = custom_fields.IdencodeField(
        related_model=form_models.Form, 
        source='criterion.verifier_form',
        read_only=True)

    class Meta:
        """Meta Info."""
        model = claim_models.NodeCriterion
        fields = (
            'criterion', 'form_submission', 'status', 'node_claim', 'form', 
            'submission_form_mongo_id', 'verifier_submission', 'verifier_form')


class NodeClaimSerializer(claim_serializers.AttachedClaimSerializer):
    """
    Serializer for company claim.
    """

    node = custom_fields.IdencodeField(
        related_model=node_models.Node, 
        serializer=node_serializers.BasicNodeSerializer, required=False)
    criteria = NodeCriterionSerializer(many=True, required=False)
    standard = serializers.CharField(required=False, write_only=True)

    class Meta:
        """
        Meta Info.
        """

        model = claim_models.NodeClaim
        fields = claim_serializers.AttachedClaimSerializer.Meta.fields + (
            'node', 'criteria', 'standard')

    def validate(self, attrs):
        """Validate company claim data."""
        if 'claim' not in attrs.keys() and 'standard' not in attrs.keys():
            raise exceptions.BadRequest(_("Claim or Standard required."))
        if 'node' not in attrs.keys():
            attrs['node'] = session.get_current_node()
        if attrs.get('standard',  None):
            attrs['claim'] = claim_models.Claim.objects.get(
                standard_id=attrs.get('standard'))
            attrs.pop('standard')
        if not attrs['claim'].attach_to_node:
            raise exceptions.BadRequest(_("Claim is not attachable to Company."))
        return super().validate(attrs)

    @django_transaction.atomic
    def create(self, validated_data):
        """
        Create overrided to create nodeclaims and nodeclaimcriterions.
        """
        current_user = session.get_current_user()
        validated_data['attached_to'] = claim_constants.ClaimAttachedTo.NODE
        validated_data['attached_by'] = session.get_current_node()
        if 'node' not in validated_data.keys():
            validated_data['node'] = session.get_current_node()
        if validated_data['claim'].verification_type == \
                claim_constants.ClaimVerificationMethod.SECOND_PARTY:
            validated_data['verifier'] = session.get_current_node()
        node_claims = claim_models.NodeClaim.objects.filter(
            node=validated_data['node'], 
            claim=validated_data['claim']
        ).exclude(status=claim_constants.ClaimStatus.REJECTED)
        if node_claims.exists():
            return node_claims.first()
        criteria = validated_data.pop('criteria', None)
        node_claim = claim_models.NodeClaim.objects.create(**validated_data)
        if criteria:
            for criterion in criteria:
                criterion['node_claim'] = node_claim
                criterion = NodeCriterionSerializer(data=criterion)
                if not criterion.is_valid():
                    raise exceptions.BadRequest(
                        _("Company criterion creation failed."))
                criterion.save()
        if validated_data.get('verifier', None):
            node_claim.notify_claim_attached()
        return node_claim
