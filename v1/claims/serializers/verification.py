
from rest_framework import serializers

from django.db import transaction as django_transaction
from django.utils.translation import gettext_lazy as _

from common.drf_custom import fields as custom_fields

from base import exceptions
from base import session

from v1.claims import models as claim_models
from v1.claims.serializers.claim import AttachCriterionSerializer
from v1.claims.constants import ClaimStatus

from v1.nodes import constants as node_consts

from v1.transactions import constants as txn_consts
from v1.transactions.serializers.external import \
    ExternalTransactionRejectionSerializer

from v1.dynamic_forms import models as form_models


class  AttachedCriterionSerializer(serializers.Serializer):
    """
    Serializer to get attached criteria and their submission while 
    verifiying the claim.
    """
    attached_criterion_id = custom_fields.IdencodeField(required=False)
    verifier_submission = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission, required=False
    )


class VerificationListSerializer(serializers.ModelSerializer):
    """
    Api to list claim verifications
    """

    id = custom_fields.IdencodeField(read_only=True)
    claim = serializers.CharField(source='claim.name', read_only=True)
    assigned_by = serializers.CharField(
        source='attached_by.name', read_only=True)
    date = custom_fields.UnixDateField(read_only=True, source='created_on')
    
    class Meta:
        """Meta Info"""

        model = claim_models.AttachedClaim
        fields = (
            'id', 'claim', 'assigned_by', 'claim', 'supply_chain', 'product', 
            'status', 'batch_id', 'date', 'extra_info')


class VerificationSerializer(serializers.ModelSerializer):
    """
    Api to list claim verifications
    """

    id = custom_fields.IdencodeField(read_only=True)
    claim = serializers.CharField(source='claim.name', read_only=True)
    claim_description = serializers.CharField(
        source='claim.description', read_only=True)
    assigned_by = serializers.CharField(
        source='attached_by.name', read_only=True)
    criteria = AttachCriterionSerializer(
        source='claim_object.criteria', many=True, read_only=True)
    update_criteria = AttachedCriterionSerializer(
        many=True, write_only=True, required=False)
    date = custom_fields.UnixDateField(read_only=True, source='created_on')
    type = serializers.IntegerField(read_only=True, source='attached_to')
    linked_transaction_info = serializers.SerializerMethodField()
    linked_company_info = serializers.SerializerMethodField()

    
    class Meta:
        """Meta Info"""

        model = claim_models.AttachedClaim
        fields = (
            'id', 'claim', 'claim_description', 'assigned_by', 
            'batch_id', 'status', 'criteria', 'extra_info', 'note', 
            'date', 'type', 'linked_transaction_info', 'linked_company_info', 
            'update_criteria',
            )

    def get_linked_transaction_info(self, claim):
        """
        Return linked transaction detail, If the claim is linked with txn.
        """
        try:
            txn = claim.batchclaim.transaction
            txn_info = {
                "transaction_id": txn.number, 
                "date": txn.date.strftime('%d-%m-%Y'), 
                "source_company": txn.source_node.name, 
                "product": claim.batchclaim.batch.product.name
            }
        except:
            txn_info = None
        return txn_info

    def get_linked_company_info(self, claim):
        """
        Return linked transaction detail.
        """
        try:
            node = claim.claim_object.target_node()
            node_info = {
                "name": node.name, 
                "type": node.operation.name, 
                "city": node.city, 
                "country": node.country.name
            }
        except:
            node_info = None
        return node_info
    
    def validate(self, attrs):
        """
        validate given data with the instance.
        """
        node = session.get_current_node()
        approvables = [
            ClaimStatus.PENDING, 
            ClaimStatus.PARTIAL
        ]
        if self.instance.status not in approvables or \
            self.instance.verifier != node:
            raise exceptions.BadRequest(_("Can not change status"))
        try:
            member = session.get_current_user().member_nodes.get(
                node=node)
        except:
            raise exceptions.BadRequest(_("Member does not exist."))
        member_types = [
            node_consts.NodeMemberType.ADMIN, 
            node_consts.NodeMemberType.SUPER_ADMIN, 
            node_consts.NodeMemberType.TRANSACTION_MANAGER
        ]
        if member.type not in member_types:
            raise exceptions.BadRequest(_("User can not change status"))
        return super().validate(attrs)
    
    @django_transaction.atomic
    def update(self, instance, validated_data):
        """Change status of attached claim and its criterions."""
        for criterion_data in validated_data['update_criteria']:
            criterion = claim_models.AttachedCriterion.objects.get(
                id=criterion_data['attached_criterion_id'])
            criterion.verifier_submission = criterion_data.get(
                'verifier_submission', None)
            criterion.status = validated_data['status']
            criterion.updater = session.get_current_user()
            criterion.save()
        claim = super().update(instance, validated_data)
        claim.claim_object.status = validated_data['status']
        claim.claim_object.save()
        claim.notify_claim_verified()
        return claim
