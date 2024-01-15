"""Serializers related to batch claims are stored here."""

from rest_framework import serializers
from django.db import transaction as django_transaction
from django.utils.translation import gettext_lazy as _

from base import session
from base import exceptions

from common.drf_custom import fields as custom_fields

from v1.claims import models as claim_models
from v1.claims import constants as claim_constants
from v1.claims.serializers import claim as claim_serializers

from v1.dynamic_forms import models as form_models

from v1.products import models as product_models

from v1.transactions import models as txn_models
from v1.transactions import constants as txn_constants


class BatchCriterionSerializer(serializers.ModelSerializer):
    """
    Serializer for criterion and submission form.
    """

    criterion = custom_fields.IdencodeField(
        related_model=claim_models.Criterion)
    form_submission = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission)
    submission_form_mongo_id = serializers.CharField(required=False)
    status = serializers.IntegerField(required=False)
    batch_claim = custom_fields.IdencodeField(
        related_model=claim_models.BatchClaim, allow_null=True, required=False)

    class Meta:
        """Meta Info."""
        model = claim_models.BatchCriterion
        fields = (
            'criterion', 'form_submission', 'status', 'batch_claim', 
            'submission_form_mongo_id')


class BatchClaimSerializer(claim_serializers.AttachedClaimSerializer):
    """
    Serializer for company claim.
    """

    batch = custom_fields.IdencodeField(
        related_model=product_models.Batch, write_only=True, required=False, 
        allow_null=True)
    transaction = custom_fields.IdencodeField(
        related_model=txn_models.Transaction, required=False, 
        allow_null=True)
    criteria = BatchCriterionSerializer(
        many=True, required=False, write_only=True)
    verification_percentage = serializers.FloatField(required=False)

    class Meta:
        """
        Meta Info.
        """

        model = claim_models.BatchClaim
        fields = claim_serializers.AttachedClaimSerializer.Meta.fields + (
            'batch', 'criteria', 'transaction', 'verification_percentage',) 

    def validate(self, attrs):
        """Validate company claim data."""
        if not attrs['claim'].attach_to_batch:
            raise exceptions.BadRequest(
                _("Claim is not attachable to Batch or Transaction."))
        transaction = attrs.get('transaction', None)
        batch = attrs.get('batch', None)
        if transaction and not batch:
            if not attrs['claim'].attach_while_transacting:
                raise serializers.ValidationError(
                    _("This claim cannot be attached while transacting."))
        if batch and not transaction:
            if not attrs['claim'].attach_from_batch_details:
                raise serializers.ValidationError(
                    _("This claim cannot be attached directly to batch."))
        return super().validate(attrs)

    @django_transaction.atomic
    def create(self, validated_data):
        """
        Create overrided to create nodeclaims and nodeclaimcriterions.
        """
        transaction = validated_data.get('transaction', None)
        batch = validated_data.get('batch', None)
        if transaction and not batch:
            for batch in transaction.result_batches.all():
                validated_data['batch'] = batch
                sub_bsc = BatchClaimSerializer(data=validated_data, context=self.context)
                if not sub_bsc.is_valid():
                    raise serializers.ValidationError(sub_bsc.errors)
                sub_bsc.save()

        current_user = session.get_current_user()
        validated_data['attached_to'] = claim_constants.ClaimAttachedTo.BATCH
        validated_data['creator'] = current_user
        validated_data['updater'] = current_user
        validated_data['attached_by'] = session.get_current_node()
        batch_claims = claim_models.BatchClaim.objects.filter(
            batch=validated_data['batch'], 
            claim=validated_data['claim'])
        if batch_claims.exists():
            return batch_claims.first()
        criteria = validated_data.pop('criteria', None)
        if validated_data['claim'].verification_type == \
            claim_constants.ClaimVerificationMethod.SECOND_PARTY:
            validated_data['verifier'] = validated_data['batch'].node
        batch_claim = super().create(validated_data)
        if criteria:
            for criterion in criteria:
                criterion['batch_claim'] = batch_claim
                criterion = BatchCriterionSerializer(data=criterion)
                if not criterion.is_valid():
                    raise exceptions.BadRequest(
                        _("Batch criterion creation failed."))
                criterion.save()
        if batch_claim.attached_via == claim_constants.ClaimAttachedVia.INHERITANCE:
            batch_claim.approve_inherited_claims()
        return batch_claim


class AttachBatchClaimSerializer(serializers.Serializer):
    """
    Serializer to create batch claim.
    """

    batch = custom_fields.IdencodeField(
        related_model=product_models.Batch, required=False, allow_null=True)
    transaction = custom_fields.IdencodeField(
        related_model=txn_models.Transaction, 
        required=False, allow_null=True, allow_blank=True)
    claims = claim_serializers.AttachedClaimSerializer(many=True)

    class Meta:
        """Meta Info."""
        fields = ('batch', 'claims', 'transaction',)

    @staticmethod
    def _add_to_intermediate_transactions(transaction, validated_data):
        fsb = transaction.source_batches.first()
        if fsb:
            st = fsb.incoming_transactions.first()
            if st and st.transaction_type == txn_constants.TransactionType.INTERNAL:
                if st.internaltransaction.mode == txn_constants.TransactionMode.SYSTEM:
                    validated_data['transaction'] = st
                    abc = AttachBatchClaimSerializer(data=validated_data)
                    abc.is_valid(raise_exception=True)
                    abc.save()


    @django_transaction.atomic
    def create(self, validated_data):
        """
        Create overrided to create claims.
        """
        batch = validated_data.get('batch', None)
        transaction = validated_data.get('transaction', None)

        if transaction:
            batches = transaction.result_batches.all()
        elif batch:
            transaction = None
            batches = [batch]
        else:
            raise AssertionError(_("Either Batch of Transaction should be passed."))

        for claim in validated_data['claims']:
            claim['transaction'] = transaction
            for batch in batches:
                claim['batch'] = batch
                batch_claim = BatchClaimSerializer(data=claim)
                if not batch_claim.is_valid():
                    raise exceptions.BadRequest(
                        _("Claim adding to batch is failed."))
                batch_claim = batch_claim.save()
                if claim.get('verifier', None):
                    batch_claim.notify_claim_attached()
        if transaction:
            self._add_to_intermediate_transactions(transaction, validated_data)
        return {"message": _("Claims added successfully")}

    def to_representation(self, instance):
        """to representation overrided to add success response."""
        data = {
            "message": _("Claims added successfully")
        }
        return data
