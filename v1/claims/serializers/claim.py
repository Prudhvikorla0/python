"""Serializers related to claim."""

from rest_framework import serializers

from django.db import transaction as django_transaction
from django.utils.translation import gettext_lazy as _

from base import session
from utilities import functions as util_functions
from base import exceptions

from common.drf_custom import fields as custom_fields
from common import library as common_lib

from v1.claims import models as claim_models
from v1.claims import constants as claim_consts

from v1.supply_chains.serializers import supply_chain
from v1.supply_chains.models import SupplyChain

from v1.nodes.serializers.node import BasicNodeSerializer, NodeDocumentSerializer
from v1.nodes.models import Node, NodeDocument

from v1.dynamic_forms.serializers.form import FormFieldSerializer, \
    FormSerializer, FieldValueSerializer
from v1.dynamic_forms import models as form_models
from v1.dynamic_forms import constants as form_consts

from v1.products import models as prod_models

from v1.accounts.serializers import user as user_serializers


class CriterionSerializer(serializers.ModelSerializer):
    """
    Serializer for claim criterion.
    """

    id = custom_fields.IdencodeField(read_only=True)
    claim = custom_fields.IdencodeField(
        related_model=claim_models.Claim, required=False)
    fields = FormFieldSerializer(many=True, write_only=True)
    form = FormSerializer(read_only=True)

    class Meta:
        """Meta Info."""
        model = claim_models.Criterion
        fields = (
            'id', 'claim', 'name', 'description', 'is_mandatory', 'version', 
            'fields', 'form')

    def create_fields(self, fields):
        """Method to create fields under the criterion."""
        current_user = session.get_current_user()
        form = form_models.Form.objects.create(
                    type=form_consts.FormType.CLAIM_FORM, 
                    creator=current_user, updater=current_user)
        for field_data in fields:
            field_data['form'] = form
            field = FormFieldSerializer(data=field_data)
            if not field.is_valid():
                raise serializers.ValidationError(_("not valid"))
            field.save()
        return form

    def create(self, validated_data):
        """
        Create overrided to add creator, updater and create 
        fields and form and assign created form to the creterion.
        """
        if 'fields' in validated_data.keys():
            validated_data['form'] = self.create_fields(
                validated_data.pop('fields'))
        return super().create(validated_data)
    

class ClaimSerializer(serializers.ModelSerializer):
    """
    Serializer for claim.
    """

    id = custom_fields.IdencodeField(read_only=True)
    supply_chains = custom_fields.ManyToManyIdencodeField(
        related_model=SupplyChain, required=False, 
        serializer=supply_chain.SupplyChainSerializer
    )
    verifiers = custom_fields.ManyToManyIdencodeField(
        related_model=Node, serializer=BasicNodeSerializer, 
        required=False)
    criteria = custom_fields.ManyToManyIdencodeField(
        serializer=CriterionSerializer, read_only=True)

    class Meta:
        """Meta Info."""

        model = claim_models.Claim
        fields = (
            'id', 'supply_chains', 'verifiers', 'name', 'description', 'type',
            'image', 'version', 'criteria', 'verification_type', 'is_removable', 
            'is_proportional', 'inheritable',
            )

    @django_transaction.atomic
    def create(self, validated_data):
        """Create overrided to assign creator and tenant."""
        validated_data['tenant'] = session.get_current_tenant()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update overrided to assign updater.
        """
        return super().update(instance, validated_data)


class ClaimBasicSerializer(serializers.ModelSerializer):
    """
    Basic claim serializer
    """

    id = custom_fields.IdencodeField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)

    class Meta:
        model = claim_models.Claim
        fields = ('id', 'name', 'description',)


class AttachCriterionSerializer(serializers.ModelSerializer):
    """
    Serializer for criterion and submission form.
    """

    id = custom_fields.IdencodeField(read_only=True)
    criterion = custom_fields.IdencodeField(
        related_model=claim_models.Criterion)
    name = serializers.CharField(
        source='criterion.name', read_only=True)
    description = serializers.CharField(
        source='criterion.description', read_only=True)
    form_submission = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission)
    submission_form_mongo_id = serializers.CharField(
        required=False, allow_null=True)
    form = custom_fields.IdencodeField(
        related_model=form_models.Form, 
        source='form_submission.form', 
        read_only=True)
    verifier_submission = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission, required=False)
    verifier_form = custom_fields.IdencodeField(
        related_model=form_models.Form, 
        source='criterion.verifier_form', 
        read_only=True)

    class Meta:
        """Meta Info."""
        model = claim_models.AttachedCriterion
        fields = (
            'id', 'criterion', 'name', 'description', 'form_submission', 'form', 
            'submission_form_mongo_id', 'verifier_submission', 'verifier_form',
            )


class AttachedClaimSerializer(serializers.ModelSerializer):
    """
    Serializer to create batch claims
    """

    id = custom_fields.IdencodeField(read_only=True)
    claim = custom_fields.IdencodeField(
        required=False, related_model=claim_models.Claim, write_only=True)
    status = serializers.IntegerField(read_only=True)
    blockchain_address = serializers.CharField(read_only=True)
    claim_id = serializers.CharField(read_only=True, source='claim.idencode')
    name = serializers.CharField(read_only=True, source='claim.name')
    type = serializers.IntegerField(read_only=True, source='attached_to')
    scope = serializers.IntegerField(read_only=True, source='claim.scope')
    description = serializers.CharField(
        read_only=True, source='claim.description')
    image = serializers.CharField(read_only=True, source='claim.image')
    verifier = custom_fields.IdencodeField(
        related_model=Node, serializer=BasicNodeSerializer, 
        required=False, allow_null=True)
    attached_by = custom_fields.IdencodeField(
        related_model=Node, serializer=BasicNodeSerializer, read_only=True)
    criteria = AttachCriterionSerializer(required=False, write_only=True, many=True)
    attached_via = serializers.IntegerField(required=False)
    attached_to = serializers.IntegerField(read_only=True)
    certified_by = serializers.CharField(required=False)
    certification_number = serializers.CharField(required=False) 
    certification_date = serializers.DateField(
        required=False, input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'))
    expiry_date = serializers.DateField(
        required=False, input_formats=('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'))
    document = serializers.FileField(required=False)
    note = serializers.CharField(required=False)
    
    class Meta:
        """Meta Info."""
        model = claim_models.AttachedClaim
        fields = (
            'id', 'claim', 'type', 'scope', 'verifier', 'attached_by', 'status',
            'blockchain_address', 'name', 'image', 'claim_id', 'attached_to',
            'description', 'criteria', 'attached_via','certified_by', 
            'certification_number', 'certification_date', 'expiry_date', 'document', 
            'note', 'document_name'
        )


class AttachedCriterionSerializer(serializers.ModelSerializer):
    """ Serializer to get the details of the criterions attached to a batch. """
    criterion_id = serializers.CharField(source='criterion.idencode')
    name = serializers.CharField(read_only=True, source='criterion.name')
    verification_type = serializers.CharField(
        read_only=True, source='criterion.verification_type')
    description = serializers.CharField(
        read_only=True, source='criterion.description')

    class Meta:
        model = claim_models.AttachedCriterion
        fields = ('criterion_id', 'name', 'description',
                  'verification_type',)


class BaseAttachedClaimSerializer(serializers.ModelSerializer):
    """
    Api to list claim
    """

    id = custom_fields.IdencodeField(read_only=True)
    claim = serializers.CharField(source='claim.name', read_only=True)
    claim_id = serializers.CharField(source='claim.idencode', read_only=True)
    claim_description = serializers.CharField(
        source='claim.description', read_only=True)
    assigned_by = serializers.CharField(
        source='attached_by.name', read_only=True)
    criteria = AttachCriterionSerializer(
        source='claim_object.criteria', many=True, read_only=True)
    verifier = BasicNodeSerializer(read_only=True)
    verification_type = serializers.IntegerField(
        source='claim.verification_type', read_only=True)

    
    class Meta:
        """Meta Info"""

        model = claim_models.AttachedClaim
        fields = (
            'id', 'claim', 'claim_id', 'claim_description', 'assigned_by', 
            'batch_id', 'transaction_id', 'status', 'criteria', 'verifier', 
            'verification_type'
            )


class BatchBaseSerializer(serializers.Serializer):
    """ Serializer for validating source products in a transaction """

    batch = custom_fields.IdencodeField(
        related_model=prod_models.Batch)
    quantity = custom_fields.RoundingDecimalField(max_digits=25, decimal_places=3)

    class Meta:
        fields = ('batch', 'quantity')

    def validate(self, attrs):
        if attrs['batch'].current_quantity < attrs['quantity']:
            raise serializers.ValidationError(
                _("Batch quantity mismatch for {batch_id}").format(batch_id=attrs['batch'].idencode))
        return attrs


class InheritableClaimSerializer(serializers.Serializer):
    """
    Serializer to list inheritable claims.
    """

    batches = BatchBaseSerializer(
        write_only=True, many=True, required=False)
    output_products = custom_fields.ManyToManyIdencodeField(
        related_model=prod_models.Product, write_only=True)

    class Meta:
        """Meta Info."""
        fields = ('batches', 'output_products',)

    def create(self, validated_data):
        products = validated_data['output_products']
        claims = set()
        batch_prods = set()
        for batch_dict in validated_data['batches']:
            batch = batch_dict['batch']
            claims.update(batch.batch_claims.filter(
                status=claim_consts.ClaimStatus.APPROVED
                ).values_list('claim', flat=True))
            batch_prods.add(batch.product.id)
        claims = claim_models.Claim.objects.filter(id__in=claims)
        inheritable_claims = []
        for claim in claims:
            if claim.inheritable == \
                    claim_consts.ClaimInheritanceType.NEVER:
                    continue
            if claim.inheritable == \
                claim_consts.ClaimInheritanceType.PRODUCT and (
                    products.count() and len(batch_prods) != 1 or \
                    products.filter(id__in=batch_prods).count() != 1):
                continue
            claim_data = {
                "claim": claim.idencode, 
                "removable": claim.is_removable, 
                "criteria": [], 
                "claim_name": claim.name
            }
            total = 0
            verified = 0
            batch_claim_data = []
            for batch_dict in validated_data['batches']:
                quantity = batch_dict['quantity']
                total += quantity
                try:
                    batch_claim = batch.batch_claims.get(claim=claim)
                    batch_claim_data.append(
                        BaseAttachedClaimSerializer(batch_claim).data)
                    verified += float(quantity) * (
                        batch_claim.verification_percentage / 100)
                except:
                    pass
            criteria_ids = []
            criterion_list = []
            for batch_data in batch_claim_data:
                if not batch_data['criteria']:
                    continue
                for criterion in batch_data['criteria']:
                    criterion_data = {}
                    if criterion['criterion'] in criteria_ids:
                        continue
                    criteria_ids.append(criterion['criterion'])
                    criterion_data['criterion'] = criterion['criterion']
                    criterion_data['form_submission'] = \
                        criterion['form_submission']
                    criterion_list.append(criterion_data)
            claim_data['criteria'] = criterion_list
            claim_data['verification_percentage'] = util_functions.percentage(
                verified, total)
            inheritable_claims.append(claim_data)
        return inheritable_claims

    def to_representation(self, claims):
        """Inheritable claims returned."""
        return {'inheritable_claims': claims}


class AttachedClaimCommentSerializer(serializers.ModelSerializer):
    """Serializer for claim comment."""

    id = custom_fields.IdencodeField(read_only=True)
    creator = custom_fields.IdencodeField(
        serializer=user_serializers.BasicUserSerializer, read_only=True)
    updater = custom_fields.IdencodeField(
        serializer=user_serializers.BasicUserSerializer, read_only=True)
    created_on = custom_fields.UnixDateField(read_only=True)
    updated_on = custom_fields.UnixDateField(read_only=True)
    company_document = custom_fields.IdencodeField(
        required=False, related_model=NodeDocument)

    class Meta:
        """
        Meta Info.
        """

        model = claim_models.AttachedClaimComment
        fields = (
            'id', 'comment', 'file', 'name', 'creator' , 'updater', 
            'created_on', 'updated_on', 'extra_info', 'company_document',
            'files'
        )

    def create(self, validated_data):
        """
        Overrided create to add creator and updater.
        """
        current_user = session.get_current_user()
        validated_data['member'] = session.get_current_node().node_members.get(
            user=current_user)
        try:
            attached_claim = claim_models.AttachedClaim.objects.get(
                id=self.context.get('view').kwargs.get('id', None))
        except:
            raise exceptions.NotFound(_("Attached claim does not exist"))
        validated_data['attached_claim'] = attached_claim
        if session.get_current_node() != attached_claim.verifier and \
            session.get_current_node() != attached_claim.attached_by:
            exceptions.BadRequest(_("User is not allowed to comment"))
        company_document = validated_data.get("company_document",None)
        if company_document:
            validated_data['file'] = company_document.file
            validated_data['name'] = company_document.name
        comment = super().create(validated_data)
        comment.notify()
        return comment

    def update(self, instance, validated_data):
        """
        Checks the updater is the owner or admin.
        Assign user into updater.
        """
        current_user = session.get_current_user()
        if current_user != instance.creator:
            raise exceptions.AccessForbidden(
                _("User is not allowed to edit comment."))
        company_document = validated_data.get("company_document",None)
        if company_document and company_document != instance.company_document:
            validated_data['file'] = company_document.file
            validated_data['name'] = company_document.name
        return super().update(instance, validated_data)
