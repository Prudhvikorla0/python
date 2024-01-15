"""Models of the app Claims."""

import json
import os
from functools import partial
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

from base.models import AbstractBaseModel
from base import session
from common.library import _get_file_path, get_random_string
from utilities.function_generators import formatter

from v1.risk.integrations.roai import apis as roai_apis
from v1.blockchain.models.submit_message import AbstractConsensusMessage
from v1.dynamic_forms import constants as df_constants
from v1.claims import constants as claim_consts
from v1.claims import notifications
from v1.nodes import constants as node_consts
from v1.nodes import models as node_models
from v1.accounts import models as user_models
from v1.accounts import constants as acc_consts

from v1.transactions import constants as txn_consts


class Claim(AbstractBaseModel):
    """
    Model to store claims.
    When a claim needs to be updated, a new claim is created with an
    incremented version number.

    Attributes:
        tenant(obj)             : tenant object who create claim.
        supply_chains(FKs)      : Which all supply chains is the claims available in.
        verifiers(FKs)          : Preset set of verifiers.
        name(char)              : Name of claim.
        description(char)       : Description of claim.
        type(int)               : Product claim or company claim.
        image(image)            : Image of the claim.
        proportional(bool)      : Whether a batch can have the claim partly.
        removable(bool)         : Whether it can removed during transaction
        inheritable(int)        : Whether the batch inherits if transferred/processed
        batch_attachemnt(bool)  : claim attachable with batch.
        txn_attachemnt(bool)    : claim attachable while doing transaction.
        verification_type(int)  : which verification method uses this claim.
            eg: self, second party, third party...
        reference(int)          : Reference number to identify multiple versions of same claim.
        version(int)            : Version number of claim.
        active(bool)            : Whether the claims is active or not. All previous
                                  versions of a claim is made inactive.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """
    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE, 
        related_name='claims', verbose_name=_('Tenant'), null=True, blank=True)
    supply_chains = models.ManyToManyField(
        'supply_chains.SupplyChain', blank=True,
        related_name='included_claims', verbose_name=_('Supply Chains'))
    verifiers = models.ManyToManyField(
        'nodes.Node', blank=True, related_name='verifiable_claims', 
        verbose_name=_('Verifiers'))
    product_types = models.ManyToManyField(
        'products.ProductType', blank=True, related_name='claims', 
        verbose_name=_('Product Types'))
    operations = models.ManyToManyField(
        'supply_chains.Operation', blank=True, 
        related_name='claims', 
        verbose_name=_('Node Operations'))
    countries = models.ManyToManyField(
        'tenants.Country', blank=True, 
        related_name='claims', 
        verbose_name=_('Countries'))
    
    name = models.CharField(max_length=500, verbose_name=_('Claim'))
    code = models.CharField(
        max_length=100, verbose_name=_('Claim Code'),
        default=partial(formatter, "{r10}"), unique=True)
    description = models.CharField(
        max_length=2000, default='', null=True, blank=True,
        verbose_name=_('Description'))

    attach_to_node = models.BooleanField(
        default=True, verbose_name=_("Can claim be attached to nodes? "
                                     "(Formerly company claims)"))
    attach_from_profile = models.BooleanField(
        default=True, verbose_name=_("Can claim be attached directly from profile."
                                     "(Relevant for company claims)."))
    attach_while_connecting = models.BooleanField(
        default=False, verbose_name=_("Can claim be attached while adding connection"
                                      "(Relevant for company claims)."))

    attach_to_batch = models.BooleanField(
        default=True, verbose_name=_("Can claim be attached to batches? "
                                     "(Formerly product claims)"))
    attach_from_batch_details = models.BooleanField(
        default=True, verbose_name=_("Can claim be attached directly from batch details."
                                     "(Relevant for product claims)."))
    attach_while_transacting = models.BooleanField(
        default=True, verbose_name=_("Can claim be attached during transaction."
                                     "(Relevant for product claims)."))
    type = models.IntegerField(
        choices=claim_consts.ClaimType.choices, 
        default=claim_consts.ClaimType.PRODUCT_CLAIM, 
        verbose_name=_('Claim Type'))
    group = models.IntegerField(
        choices=claim_consts.ClaimGroup.choices, 
        default=claim_consts.ClaimGroup.CERTIFICATION, 
        verbose_name=_('Claim Group'))
    image = models.ImageField(
        upload_to=_get_file_path, null=True, default=None, 
        blank=True, verbose_name=_('Photo'))
    is_proportional = models.BooleanField(
        default=True, verbose_name=_('Is Claim Proportional'))
    is_removable = models.BooleanField(
        default=False, verbose_name=_('Is Claim Removable'))
    inheritable = models.IntegerField(
        default=claim_consts.ClaimInheritanceType.NEVER,
        choices=claim_consts.ClaimInheritanceType.choices, 
        verbose_name=_('Claim Inheritance Type'))
    verification_type = models.IntegerField(
        default=claim_consts.ClaimVerificationMethod.NONE,
        choices=claim_consts.ClaimVerificationMethod.choices, 
        verbose_name=_('Verification Type'))
    standard_id = models.CharField(
        default='', null=True, max_length=32, verbose_name=_('Standard ID'),
        help_text=_("ID of Standard received from Risk Analysis module"))
    version = models.IntegerField(default=1, verbose_name=_('Version'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    added_by = models.IntegerField(
        default=claim_consts.ClaimAddedBy.TENANT,
        choices=claim_consts.ClaimAddedBy.choices, 
        verbose_name=_('Claim Created By'))
    verifier_can_edit = models.BooleanField(
        default=False, verbose_name=_('Verifier Can Edit Attached Evidence'))

    def __str__(self):
        """Object name in django admin."""
        return f'{self.name} - {self.tenant.name} - {self.version}'


class Criterion(AbstractBaseModel):
    """
    Model to store claim criterion.
    When a criterion needs to be updated, a new criterion is created with an
    incremented version number and the same reference number.

    Attributes:
        claim(obj)          : Claim that the criterion is associated with.
        name(char)          : Name for the criterion.
        description(char)   : Description for the criterion.
        is_mandatory(bool)  : Whether it is a mandatory criterion
        verification_type(int)  : Verified by system or manually
        reference(int)      : Reference number to identify multiple versions
                              of same criterion.
        version(int)        : Version number of criterion.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    claim = models.ForeignKey(
        Claim, on_delete=models.CASCADE, related_name='criteria', 
        verbose_name=_('Claim'))
    name = models.CharField(
        default='', max_length=500, null=True, blank=True, 
        verbose_name=_('Claim Criterion'))
    description = models.TextField(
        default='', blank=True, null=True, verbose_name=_('Description'))
    is_mandatory = models.BooleanField(
        default=False, verbose_name=_('Is Criterion Mandatory'))
    verification_type = models.IntegerField(
        default=claim_consts.ClaimVerificationType.SYSTEM,
        choices=claim_consts.ClaimVerificationType.choices, 
        verbose_name=_('Verification Type'))
    reference = models.CharField(
        default='', null=True, max_length=16, verbose_name=_('Reference Number'))
    version = models.IntegerField(
        default=1, verbose_name=_('Version Of Criterion'))
    form = models.ForeignKey(
        'dynamic_forms.Form', on_delete=models.SET_NULL, related_name='attatched_criterion', 
        verbose_name=_('Fields'), blank=True, null=True)
    verifier_form = models.ForeignKey(
        'dynamic_forms.Form', on_delete=models.SET_NULL, related_name='verifer_criterion', 
        verbose_name=_('Verifer Form'), blank=True, null=True)
    

    class Meta:
        verbose_name_plural = _('Criteria')

    def __str__(self):
        """Object name in django admin."""
        return f'{self.name} - {self.claim.name} - {self.idencode}'


class AttachedClaim(AbstractBaseModel, AbstractConsensusMessage):
    """
    Base model for all attached claims, for product claims as well as company 
    claims. For production claims, the claims will be attached to the batch
    and for company claims, it will be attached to a node.

    Attribs:
        claim(obj)          : Attached claim.
        verifier(obj)       : verifier of the claim.
        attached_by(obj)    : company which attached the claim.
        status(int)         : status of the claim(approved, rejected...)
        note(text)          : any notes about the claim attachment.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """
    claim = models.ForeignKey(
        Claim, on_delete=models.CASCADE, verbose_name=_('Attached Claim'),
        related_name='attached_claims')
    attached_to = models.IntegerField(
        choices=claim_consts.ClaimAttachedTo.choices,
        default=claim_consts.ClaimAttachedTo.BATCH,
        verbose_name=_('Claim Attached to'))
    verifier = models.ForeignKey(
        'nodes.Node', blank=True, null=True, default=None,
        on_delete=models.SET_NULL, related_name='claim_verifications',
        verbose_name=_('Claim Verifier'))
    attached_by = models.ForeignKey(
        'nodes.Node', blank=True, null=True, default=None,
        on_delete=models.SET_NULL, related_name='claims_attached',
        verbose_name=_('Claim Attached By'))
    status = models.IntegerField(
        choices=claim_consts.ClaimStatus.choices,
        default=claim_consts.ClaimStatus.PENDING,
        verbose_name=_('Claim Current Status'))
    note = models.TextField(
        default="", null=True, blank=True, verbose_name=_('Notes'))
    attached_via = models.IntegerField(
        choices=claim_consts.ClaimAttachedVia.choices,
        default=claim_consts.ClaimAttachedVia.MANUAL,
        verbose_name=_('Attached Via'))

    certified_by = models.CharField(
        max_length=2000, default="", null=True, blank=True,
        verbose_name=_("Certification Body"),
        help_text=_("Name of the Certification body that has Issues/Approved the Claim"))
    certification_number = models.CharField(
        max_length=200, default="", null=True, blank=True,
        verbose_name=_("Certification Number"),
        help_text=_("Reference number of the certification"))
    certification_date = models.DateField(
        default=None, null=True, blank=True, verbose_name=_("Certification Date"),
        help_text=_("Date on which the item was certified."))
    expiry_date = models.DateField(
        default=None, null=True, blank=True, verbose_name=_("Expiry Date"),
        help_text=_("Date of expiry of the certification/claim"))
    document = models.FileField(
        upload_to=_get_file_path, blank=True, null=True,
        verbose_name=_("Certificate Document"))
    certification_id = models.CharField(
        max_length=100, default='', 
        verbose_name=_("Certificate Id From RO-AI"), null=True, 
        blank=True)

    def __str__(self):
        """Object name in django admin."""
        return f"{self.claim.name} | {self.id}"

    def save(self, *args, **kwargs):
        """
        """
        auto_approvals = [
            claim_consts.ClaimVerificationMethod.NONE, 
            claim_consts.ClaimVerificationMethod.SYSTEM]
        if self.claim.verification_type in auto_approvals:
            self.status = claim_consts.ClaimStatus.APPROVED
        return super().save(*args, **kwargs)

    @property
    def claim_object(self): #TODO: REWORK
        """
        returns child object of the claim.
        """
        try:
            return self.batchclaim
        except:
            pass
        try:
            return self.connectionclaim
        except:
            pass
        try:
            return self.nodeclaim
        except:
            pass
        return None

    @property
    def supply_chain(self) -> str:
        """return supply-chain of product claim"""
        if self.attached_to == claim_consts.ClaimAttachedTo.BATCH:
            return self.batchclaim.batch.product.supply_chain.name
        return ""

    def supply_chain_object(self):
        """return supply-chain of product claim"""
        if self.attached_to == claim_consts.ClaimAttachedTo.BATCH:
            return self.batchclaim.batch.product.supply_chain
        else:
            return None

    @property
    def product(self) -> str:
        """return supply-chain of product claim"""
        if self.attached_to == claim_consts.ClaimAttachedTo.BATCH:
            return self.batchclaim.batch.product.name
        else:
            return ""

    @property
    def batch_id(self):
        """return supply-chain of product claim"""
        if self.attached_to == claim_consts.ClaimAttachedTo.BATCH:
            return self.batchclaim.batch.number
        else:
            return None

    @property
    def transaction_id(self):
        """return supply-chain of product claim"""
        if self.attached_to == claim_consts.ClaimAttachedTo.BATCH:
            if self.batchclaim.transaction:
                return self.batchclaim.transaction.number
        return None

    def get_node(self):
        """Return node"""
        if self.attached_to == claim_consts.ClaimAttachedTo.NODE:
            return self.nodeclaim.node
        elif self.attached_to == claim_consts.ClaimAttachedTo.BATCH:
            return self.batchclaim.batch.node
        elif self.attached_to == claim_consts.ClaimAttachedTo.CONNECTION:
            return self.connectionclaim.connection.target
        else:
            return None

    def get_batch(self):
        """Return linked batch object"""
        if self.attached_to == claim_consts.ClaimAttachedTo.BATCH:
            return self.batchclaim.batch
        else:
            return None

    @property
    def topic_id(self):
        return self.claim.tenant.topic_id

    @property
    def message(self):
        return json.dumps(self.claim_object.claim_info(), cls=DjangoJSONEncoder)

    def claim_info(self):
        info = {
            'claim': self.claim.name,
            'claim_id': self.claim.idencode,
            'criteria': []
        }
        for criterion in self.criteria.all():
            evidences = []
            for resp in criterion.form_submission.field_values.all():
                evidence = {'name': resp.field.label}
                if resp.field.type == df_constants.FieldType.FILE:
                    evidence['file_hash'] = resp.file_hash
                else:
                    evidence['value'] = resp.response
                evidences.append(evidence)
            info['criteria'].append({
                'name': criterion.criterion.name,
                'data': evidences
            })
        return info

    def notify_claim_attached(self):
        """Method notifies verifier that claim is attached.."""
        if not self.verifier:
            return False
        for user in self.verifier.members.all():
            notification_manager = notifications.ClaimAddedNotificationManager(
                user=user, action_object=self.claim_object, token=None)
            notification_manager.send_notification()
        return True

    def notify_claim_verified(self):
        """Method notifies claim attached nodes that the claims are verified."""
        if not self.verifier:
            return False
        for user in self.get_node().members.all():
            notification_manager = notifications.ClaimVerifiedNotificationManager(
                user=user, action_object=self.claim_object, token=None)
            notification_manager.send_notification()
        return True

    def extra_info(self):
        """
        Return extra info like logged in user can accept/reject this claim.
        """
        info = {
            "can_approve": False, 
            "can_reject": False
        }
        try:
            member = session.get_current_user().member_nodes.get(
                node=self.verifier)
        except:
            return info
        member_types = [
            node_consts.NodeMemberType.ADMIN, 
            node_consts.NodeMemberType.SUPER_ADMIN, 
            node_consts.NodeMemberType.TRANSACTION_MANAGER
        ]
        claim_statuses = [
            claim_consts.ClaimStatus.PENDING, 
            claim_consts.ClaimStatus.PARTIAL
        ]
        if member.type in member_types and self.status in claim_statuses:
            info = {
            "can_approve": True, 
            "can_reject": True
            }
        return info

    def approve_inherited_claims(self):
        """
        Method approves the attached claim and it's attached criteria ,
        if it's inherited.
        """
        if self.attached_via == claim_consts.ClaimAttachedVia.INHERITANCE:
            self.status = claim_consts.ClaimStatus.APPROVED
            self.save()
            self.claim_object.criteria.all().update(
                status=claim_consts.ClaimStatus.APPROVED)
        return True

    def reject_claim(self, note=None):
        """
        Method rejects the attached claim and it's attached criteria
        """
        self.status = claim_consts.ClaimStatus.REJECTED
        if note:
            self.note = note
        self.save()
        self.claim_object.criteria.all().update(
            status=claim_consts.ClaimStatus.REJECTED)
        return True
    
    @property
    def document_name(self):
        """
        Document name.
        """
        try:
            name = os.path.basename(self.document.name).split('.')[0]
            return name[10:]
        except:
            return ''


class BatchClaim(AttachedClaim):
    """
    Claims attached with batch are stored here.

    Attribs:
        transaction(obj): Claim attached transaction.

    Inherited Attribs:
        claim(obj)          : Attached claim.
        verifier(obj)       : verifier of the claim.
        attached_by(obj)    : company which attached the claim.
        status(int)         : status of the claim(approved, rejected...)
        note(text)          : any notes about the claim attachment.

        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """
    batch = models.ForeignKey(
        'products.Batch', on_delete=models.CASCADE, 
        related_name='batch_claims', 
        verbose_name=_('Claim Attached Batch'))
    transaction = models.ForeignKey(
        'transactions.Transaction', on_delete=models.CASCADE, 
        related_name='batch_claims', verbose_name=_('Transaction'), 
        null=True, blank=True)
    verification_percentage = models.FloatField(default=0)

    def __str__(self):
        """Object name in django admin."""
        return f'{self.claim.name} - {self.idencode}'

    def claim_info(self):
        """ Additional info that is to be logged into blockchain """
        info = super(BatchClaim, self).claim_info()

        info['owner_id'] = self.batch.node.idencode
        info['owner_name'] = self.batch.node.name
        info['stock_id'] = self.batch.number
        info['product_name'] = self.batch.product.name
        info['supply_chain'] = self.batch.product.supply_chain.name

        return info


class NodeClaim(AttachedClaim):
    """
    Claims attached with company / node are saved here.

    Attribs:
        node(obj) : Claim attached company / node.

    Inherited Attribs:
        claim(obj)          : Attached claim.
        verifier(obj)       : verifier of the claim.
        attached_by(obj)    : company which attached the claim.
        status(int)         : status of the claim(approved, rejected...)
        note(text)          : any notes about the claim attachment.

        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    node = models.ForeignKey(
        'nodes.Node', on_delete=models.CASCADE, 
        related_name='node_claims', verbose_name=_('Company'))

    def __str__(self):
        """Object name in django admin."""
        return f'{self.claim.name} - {self.idencode}'

    def save(self, *args, **kwargs):
        super(NodeClaim, self).save(*args, **kwargs) # TODO: Issue in save fixed.
        if self.status == claim_consts.ClaimStatus.APPROVED:
            try:
                response = roai_apis.AddStandard(self).call()
                NodeClaim.objects.filter(id=self.id).update(certification_id=response['id'])
                self.node.initialize_risk_score()
            except:
                pass
        return self

    def claim_info(self):
        info = super(NodeClaim, self).claim_info()

        info['node_id'] = self.node.idencode
        info['node_name'] = self.node.name

        return info
    
    def target_node(self):
        """
        """
        return self.node
    

class ConnectionClaim(AttachedClaim):
    """
    Claims attached to node connections.

    Attribs:
        connection(obj): connection object.
    """

    connection = models.ForeignKey(
        'supply_chains.Connection', default=None,
        on_delete=models.CASCADE, related_name='connection_claims',
        verbose_name=_('Connection'))

    def __str__(self):
        """Object name in django admin."""
        return f'{self.claim.name} - {self.idencode}'
    
    def target_node(self):
        """
        Return claim targeted node.
        """
        return self.connection.target


class AttachedCriterion(AbstractBaseModel):
    """
    Base model for all attached criterions, both company and product.

    Attribs:
        criterion(obj)  : attached criterion.
        status(obj)     : status of the attached criterion.
        form(obj)       : extra field values of the criterion.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """
    criterion = models.ForeignKey(
        Criterion, on_delete=models.CASCADE, 
        related_name='attached_criteria', verbose_name=_('Criterion'))
    status = models.IntegerField(
        choices=claim_consts.ClaimStatus.choices,
        default=claim_consts.ClaimStatus.PENDING, 
        verbose_name=_('Current Status'))
    form_submission = models.ForeignKey(
        'dynamic_forms.FormSubmission', on_delete=models.SET_NULL, 
        related_name='attached_criterion', verbose_name=_('Extra Form Data'), 
        null=True, blank=True)
    submission_form_mongo_id = models.CharField(
        max_length=100, default='', null=True, blank=True, 
        verbose_name=_('MongoDB Form Submission Id'))
    verifier_submission = models.ForeignKey(
        'dynamic_forms.FormSubmission', on_delete=models.SET_NULL, 
        related_name='verifier_criterion', verbose_name=_('Verifier Form Data'), 
        null=True, blank=True)
    verifier_submission_mongo_id = models.CharField(
        max_length=100, default='', null=True, blank=True, 
        verbose_name=_('MongoDB Form Submission Id'))
    attached_via = models.IntegerField(
        choices=claim_consts.ClaimAttachedVia.choices,
        default=claim_consts.ClaimAttachedVia.MANUAL,
        verbose_name=_('Attached Via'))

    class Meta:
        """Meta Info."""
        verbose_name_plural = _('Attached criteria')

    def __str__(self):
        """Object name in django admin."""
        return f"{self.criterion.name} - {self.idencode}"

    def save(self, *args, **kwargs):
        """
        """
        if self.criterion.verification_type == claim_consts.ClaimVerificationType.SYSTEM:
            self.status = claim_consts.ClaimStatus.APPROVED
        return super().save(*args, **kwargs)


class BatchCriterion(AttachedCriterion):
    """ 
    Model for attaching critetion to batch through attached batch 
    criterion

    Attribs:
        batch_claim(obj)    : Criterion attached batch claim.

    Inherited Attribs:
        criterion(obj)  : attached criterion.
        status(obj)     : status of the attached criterion.
        form(obj)       : extra field values of the criterion.

        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """
    batch_claim = models.ForeignKey(
        BatchClaim, on_delete=models.CASCADE, related_name='criteria', 
        verbose_name=_('Criterion Attached Batch Claim'))

    class Meta:
        verbose_name_plural = _('Attached batch criteria')

    def __str__(self):
        """Object name in django admin."""
        return f'{self.criterion.name} - {self.idencode}'


class NodeCriterion(AttachedCriterion):
    """
    Model to store company claim criterion.
   
   Attribs:
        node_claim(obj)    : Criterion attached company claim.

    Inherited Attribs:
        criterion(obj)  : attached criterion.
        status(obj)     : status of the attached criterion.
        form(obj)       : extra field values of the criterion.

        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """
    node_claim = models.ForeignKey(
        NodeClaim, on_delete=models.CASCADE, related_name='criteria',
        verbose_name=_('Criterion Attached Company Claim'))

    def __str__(self):
        """Object name in django admin."""
        return f'{self.criterion.name} - {self.node_claim.node.name} - \
            {self.idencode}'
    

class ConnectionCriterion(AttachedCriterion):
    """
    Model to store company claim criterion.
   
   Attribs:
        node_claim(obj)    : Criterion attached company claim.

    Inherited Attribs:
        criterion(obj)  : attached criterion.
        status(obj)     : status of the attached criterion.
        form(obj)       : extra field values of the criterion.

        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """
    connection_claim = models.ForeignKey(
        ConnectionClaim, on_delete=models.CASCADE, related_name='criteria',
        verbose_name=_('Criterion Attached To Connection'))

    def __str__(self):
        """Object name in django admin."""
        return f'{self.criterion.name} - {self.connection_claim.connection.name} - \
            {self.idencode}'

    
class AttachedClaimComment(AbstractBaseModel):
    """
    Model to save comments related to a attached claim
    which incudes text nd document.
    """

    attached_claim = models.ForeignKey(
        AttachedClaim, related_name='comments',
        on_delete=models.CASCADE, verbose_name=_('Claim'))
    comment = models.TextField(
        default='', null=True, blank=True, verbose_name=_('Comment'))
    name = models.CharField(
        max_length=500, default='', null=True, blank=True, 
        verbose_name=_('Document Name'))
    file = models.FileField(
        upload_to=_get_file_path,
        null=True, default=None, blank=True, max_length=500, 
        verbose_name=_('Document'))
    member = models.ForeignKey(
        'nodes.NodeMember', on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='claim_comments', verbose_name=_('Commenter'))
    company_document = models.ForeignKey('nodes.NodeDocument', 
        on_delete=models.CASCADE, null=True, blank=True, 
        related_name='node_document')

    def __str__(self) -> str:
        """Object name in django admin."""
        return f'{self.attached_claim} - {self.name} - {self.idencode}'
    
    @property
    def file_url(self):
        """Get file url name."""
        try:
            return self.file.url
        except:
            None
    
    def files(self):
        """
        Get file from file field or if company document get if from 
        company document
        """
        if self.company_document:
            return self.company_document.file_url
        else:
            return self.file_url

    def extra_info(self):
        """
        Method return extra data about the current user can alter the 
        attached claim object or not.
        """
        member = session.get_current_node().node_members.get(
            user=session.get_current_user())
        info = {
            "can_delete": False
        }
        if member == self.member:
            info['can_delete'] = True
        return info

    def notify(self):
        """
        Notify members of the verifier or claim attacher about the comment.
        """
        node = self.attached_claim.verifier
        if self.member.node == self.attached_claim.verifier:
            node = self.attached_claim.attached_by
        if not node:
            return False
        for user in node.members.all():
            notification_manager = notifications.ClaimCommentNotificationManager(
                user=user, action_object=self, token=None)
            notification_manager.send_notification()
        return True


class ClaimTransactionType(AbstractBaseModel):
    """
    Model to store claim related to transaction type.
    """

    claim = models.ForeignKey(
        Claim, on_delete=models.CASCADE, verbose_name=_('Claim'),
        related_name='txn_types')
    main_txn_type = models.IntegerField(
        choices=txn_consts.TransactionType.choices,
        default=txn_consts.TransactionType.EXTERNAL,
        blank=True, verbose_name=_('Main Transaction Type')
    )
    child_txn_type = models.IntegerField(
        choices=claim_consts.ClaimTransactionType.choices,
        default=None,
        blank=True, verbose_name=_('Child Transaction Type'))
    
    class Meta:
        unique_together = ('claim', 'main_txn_type', 'child_txn_type')
    

    def __str__(self):
        """Function to return value in django admin."""
        return f'{self.claim.name} - {self.get_child_txn_type_display()}'
