"""Models of the app Supplychains."""

import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from base import session
from base.models import AbstractBaseModel, Address, NumberedModel
from common.library import _get_file_path
from utilities import functions as utils_functions
from functools import partial
from utilities.function_generators import formatter

from v1.accounts import constants as acc_constants
from v1.accounts.models import ValidationToken

from v1.nodes import notifications
from v1.nodes import constants as node_consts

from v1.supply_chains import constants as supply_consts
from v1.supply_chains import models as sc_models

from v1.risk.integrations.roai import apis as roai_apis

from v1.claims import constants as claim_consts


class Node(AbstractBaseModel, Address, NumberedModel):
    """
    Base model for every type of nodes.

    Attribs:
        tenant(obj)     : tenant where the node memeber belong.
        operations(objs): the categories of the node. like farmer, collector..
        name(char)      : name of the node.
        registration_no(char) : identification number of the node.
        type(int)       :type of the node(producer/company)
        contact_name(char): contact person name.
        email(email)    : email of the node.
        phone(char)     : phone number of the node.
        description(char): description about the node.
        image(image)    : image of the node.
        invited_on(date): node invited date.
        joined_on(date) : node joined date into the system.
        status(int)     : current status of the node.
        verified(bool)  : is the node verification completed or not.
        is_producer(bool): is the node can produce stocks.
        is_verifier(bool): is this node is verifier or not.
    """
    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE,
        related_name='nodes', verbose_name=_('Tenant'))
    submission_form = models.ForeignKey(
        'dynamic_forms.FormSubmission', on_delete=models.SET_NULL,
        related_name='submitted_node', null=True, blank=True,
        verbose_name=_('Extra Form Data'))
    submission_form_mongo_id = models.CharField(
        max_length=100, default='', null=True, blank=True, 
        verbose_name=_('MongoDB Form Submission Id'))
    inviter_questionnaire = models.ForeignKey(
        'dynamic_forms.FormSubmission', on_delete=models.SET_NULL,
        related_name='invited_node_questionnaire', null=True, blank=True,
        verbose_name=_('Extra Form Data'))
    inviter_questionnaire_mongo_id = models.CharField(
        max_length=100, default='', null=True, blank=True, 
        verbose_name=_('Inviter Questionnaire Mongo Submission Id'))
    signup_questionnaire = models.ForeignKey(
        'dynamic_forms.FormSubmission', on_delete=models.SET_NULL,
        related_name='self_signup_questionnaire', null=True, blank=True,
        verbose_name=_('Extra Form Data'))
    signup_questionnaire_mongo_id = models.CharField(
        max_length=100, default='', null=True, blank=True, 
        verbose_name=_('SignUp Questionnaire Mongo Submission Id'))
    operation = models.ForeignKey(
        'supply_chains.Operation', related_name='nodes',
        default=None, blank=True, verbose_name=_('Categories'),
        on_delete=models.SET_NULL, null=True)
    env_data = models.ForeignKey(
        'dynamic_forms.FormSubmission', on_delete=models.SET_NULL,
        related_name='env_data_node', null=True, blank=True,
        verbose_name=_('Environment Data'))
    env_data_mongo_id = models.CharField(
        max_length=100, default='', null=True, blank=True, 
        verbose_name=_('Environment Data Mongo Submission Id'))
    soc_data = models.ForeignKey(
        'dynamic_forms.FormSubmission', on_delete=models.SET_NULL,
        related_name='soc_data_node', null=True, blank=True,
        verbose_name=_('Social Data'))
    soc_data_mongo_id = models.CharField(
        max_length=100, default='', null=True, blank=True, 
        verbose_name=_('Scial Data Mongo Submission Id'))
    gov_data = models.ForeignKey(
        'dynamic_forms.FormSubmission', on_delete=models.SET_NULL,
        related_name='gov_data_node', null=True, blank=True,
        verbose_name=_('Governance Data'))
    gov_data_mongo_id = models.CharField(
        max_length=100, default='', null=True, blank=True, 
        verbose_name=_('Governance Data Mongo Submission Id'))

    name = models.CharField(
        max_length=500, default='', null=True, blank=True,
        verbose_name=_('Node Name'))
    trace_code = models.CharField(
        max_length=500, default=partial(formatter, node_consts.TRACE_CODE_FORMAT),
        verbose_name=_('Right Origins Traceability Code'))
    ro_number = models.CharField(
        max_length=500, default='', null=True, blank=True,
        verbose_name=_('Right Origins Identity Number'))
    registration_no = models.CharField(
        max_length=500, default='', null=True, blank=True,
        verbose_name=_('Node Registartion Number'))
    connect_id = models.CharField(
        max_length=100, default=partial(formatter, node_consts.CONNECT_ID_FORMAT),
        verbose_name=_('Connect-ID. Used to securely connect to a un related node.'))
    type = models.IntegerField(
        default=node_consts.NodeType.COMPANY,
        choices=node_consts.NodeType.choices, verbose_name=_('Node Type'))
    contact_name = models.CharField(
        max_length=500, default='', null=True, blank=True,
        verbose_name=_('Contact Person Name'))
    email = models.EmailField(
        max_length=100, blank=True, null=True, verbose_name=_('Email Name'))
    phone = models.CharField(
        max_length=50, default='', null=True, blank=True, verbose_name=_('Phone Number'))
    description = models.CharField(
        max_length=500, default='', null=True, blank=True, verbose_name=_('Description'))
    image = models.ImageField(
        upload_to=_get_file_path, null=True, default=None, blank=True,
        verbose_name=_('Photo'))
    invited_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, related_name='invited_nodes',
        null=True, blank=True, verbose_name=_('Invited By'))
    invited_on = models.DateTimeField(
        null=True, blank=True, default=None, verbose_name=_('Invited Date'))
    joined_on = models.DateTimeField(
        null=True, blank=True, default=None, verbose_name=_('Joining Date'))
    status = models.IntegerField(
        default=node_consts.NodeStatus.INACTIVE,
        choices=node_consts.NodeStatus.choices,
        verbose_name=_('Node Current Status'))
    is_verified = models.BooleanField(
        default=False, verbose_name=_('Is Node Verified'))
    is_producer = models.BooleanField(
        default=False, verbose_name=_('Is Node Producer'))
    is_verifier = models.BooleanField(
        default=False, verbose_name=_('Is Node Verifier'))
    members = models.ManyToManyField(
        'accounts.CustomUser', related_name='nodes',
        verbose_name=_('Member Nodes'),
        through='nodes.NodeMember', through_fields=('node', 'user'))
    # country = models.ForeignKey(
    #     'tenants.Country', on_delete=models.SET_NULL,
    #     related_name='located_nodes', null=True, blank=True,
    #     verbose_name=_('Country of Node'))
    province = models.ForeignKey(
        'tenants.Province', on_delete=models.SET_NULL,
        related_name='located_nodes', null=True, blank=True,
        verbose_name=_('Province of Node'))
    connections = models.ManyToManyField(
        'self', related_name='incoming_connections',
        verbose_name=_('Node Connections'), symmetrical=False,
        through='supply_chains.Connection', through_fields=('source', 'target')
    )
    incharge = models.ForeignKey(
        'accounts.CustomUser', null=True, on_delete=models.SET_NULL,
        blank=True, related_name="managing_nodes", verbose_name=_("Incharge"))
    currency = models.ForeignKey(
        'tenants.Currency', null=True, on_delete=models.SET_NULL,
        blank=True, related_name="using_nodes",
        verbose_name=_("Default Currency"))
    is_discoverable = models.BooleanField(
        default=False, verbose_name=_(
            'Is Node Discoverable To Others. '
            'Will always be discoverable with Connect-ID')
    )
    visibility = models.IntegerField(
        default=node_consts.NodeVisibilityType.TENANT_SPECIFIC,
        choices=node_consts.NodeVisibilityType.choices,
        verbose_name=_('Node Visibility'))
    upload_timestamp = models.CharField(verbose_name=_('Upload Id'),
                                        max_length=255, null=True, blank=True)
    company_url = models.URLField(
        verbose_name=_('Company Website Url'),null=True,blank=True,
        default='')

    def __str__(self):
        """Object name in django admin."""
        return f'{self.name} - {self.type}'

    def save(self, *args, **kwargs):
        """
        Override to set created_on to corresponding timestamp in upload_timestamp
        """
        if self.upload_timestamp:
            try:
                self.created_on = timezone.make_aware(
                    datetime.datetime.fromtimestamp(int(self.upload_timestamp)))
            except Exception as ex:
                print(ex)
        if not self.id and self.tenant.risk_analysis:
            super(Node, self).save(*args, **kwargs)
            self.initialize_risk_score()
        else:
            super(Node, self).save(*args, **kwargs)

    @property
    def country(self):
        if self.province:
            return self.province.country
        return None

    @property
    def risk_score(self):
        return self.risk_scores.all().order_by('-year').first()
    
    def get_risk_score(self):
        """
        Return risk score.
        """
        try:
            score = self.risk_score.overall
        except:
            score = 0
        return score

    @property
    def overall_risk_level(self):
        risk_score = self.risk_score
        return risk_score.overall_risk_level if risk_score else None

    def get_connections(
            self, supply_chain=None, buyers=True, suppliers=True,
            include_revoked=False, manual=False,supplied=False):
        """
        If exlude and supply_chain come together all the connections with 
        the supplychain are excluded.
        """
        assert buyers or suppliers, "Either sent or received should be True"
        nodes = Node.objects.filter(target_connections__source=self).annotate(
            is_buyer=models.F('target_connections__is_buyer'),
            is_supplier=models.F('target_connections__is_supplier'),
            supply_chain_id=models.F('target_connections__supply_chain__id'),
            connection_status=models.F('target_connections__status'),
            connection_id=models.F('target_connections__id'),
            initiation=models.F('target_connections__initiation')
        )
        if not suppliers:
            nodes = nodes.exclude(is_supplier=False)
        if not buyers:
            nodes = nodes.exclude(is_buyer=False)
        if supply_chain:
            sc_id = supply_chain if isinstance(
                supply_chain, int) else supply_chain.id
            nodes = nodes.filter(supply_chain_id=sc_id)
        if not include_revoked:
            nodes = nodes.exclude(
                connection_status=supply_consts.ConnectionStatus.REVOKED)
        if manual:
            nodes = nodes.filter(
                initiation=supply_consts.ConnectionInitiation.MANUAL)
        if supplied:
            nodes = nodes.filter(outgoing_transactions__destination=self)
        return nodes.order_by().order_by('-id').distinct('id')
    
    def get_connection_circle(self,sc=None):
        """
        Method returns node's connection's ids including current node's id
        """
        nodes = self.get_connections(supply_chain=sc) | Node.objects.filter(
            id=self.id).distinct('id')
        return nodes

    def activate_connections(self):
        """method activates all connections of the node."""
        self.target_connections.filter(
            status=supply_consts.ConnectionStatus.PENDING).update(
                status=supply_consts.ConnectionStatus.APPROVED)
        return True

    @property
    def profile_completion(self):
        total = 0
        filled = 0
        for field in node_consts.COMPANY_PROFILE_FIELDS:
            if type(field) == str:
                value = getattr(self, field)
                total += 1
                if value:
                    filled += 1
            elif type(field == dict):
                for fk, sub_keys in field.items():
                    if not getattr(self, fk, None):
                        total += len(sub_keys)
                        continue
                    for sub_key in sub_keys:
                        value = getattr(getattr(self, fk), sub_key)
                        total += 1
                        if value:
                            filled += 1
        return int(utils_functions.percentage(filled, total))

    def can_be_edited_by(self, node=None):
        node = node or session.get_current_node()
        if not node:
            return False
        if self.status != node_consts.NodeStatus.INACTIVE:
            return False
        if self.invited_by != node:
            return False
        return True

    def get_tracker_theme(self):
        """"""
        theme = self.tracker_theme.first()
        if not theme:
            theme = self.tenant.tracker_themes.first()
        return theme

    def refresh_connect_id(self):
        self.connect_id = formatter(node_consts.CONNECT_ID_FORMAT)
        self.save()

    def initialize_risk_score(self):
        from v1.risk import models as risk_models
        risk_models.RiskScore.update_node_score(self)
        return True

    def get_recommended_certifications(self, limit=100, offset=0):
        if not self.ro_number:
            self.initialize_risk_score()
        return roai_apis.GetRecommendedStandards(
            self.ro_number).call(limit=limit, offset=offset)

    def get_added_certifications(self, limit=100, offset=0):
        if not self.ro_number:
            self.initialize_risk_score()
        return roai_apis.GetAddedCertificates(
            self.ro_number).call(limit=limit, offset=offset)
    
    @property
    def ro_ai_certifications(self):
        """
        Method returns certifications from ro-ai.
        """
        certifications = self.node_claims.filter(
                claim__added_by=claim_consts.ClaimAddedBy.RO_AI)
        return certifications

    def get_t1_having_connections(self,sc=None,connections=None):
        """
        Method returns connections with t1 connections.
        """
        if not connections:
            connections = self.get_connections(supply_chain=sc)
        t1_having_connections = sc_models.Connection.objects.filter(
                source__in=connections, 
                initiation=supply_consts.ConnectionInitiation.MANUAL
                ).order_by('source__id').distinct('source__id')
        return t1_having_connections


class NodeMember(AbstractBaseModel):
    """
    Model saves members under nodes.

    Attribs:
        tenant(obj)     : tenant where the node memeber belong.
        user(obj)       : user account object of the node member.
        node(obj)       : node which the member is related.
        type(int)       : member type of the node member like admin, 
            operator...
        active(bool)    : is the unit still active or not.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE,
        related_name='node_members', verbose_name=_('Tenant'))
    user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.CASCADE,
        related_name='member_nodes', verbose_name=_('Member User'))
    node = models.ForeignKey(
        'nodes.Node', on_delete=models.CASCADE,
        related_name='node_members', verbose_name=_('Node'))
    submission_form = models.ForeignKey(
        'dynamic_forms.FormSubmission', on_delete=models.SET_NULL,
        related_name='node_member', verbose_name=_('Extra Form Data'),
        null=True, blank=True)
    type = models.IntegerField(
        default=node_consts.NodeMemberType.ADMIN,
        choices=node_consts.NodeMemberType.choices,
        verbose_name=_('Member Type'))
    is_active = models.BooleanField(
        default=True, verbose_name=_('Is Member Active'))
    default_supply_chain = models.ForeignKey(
        'supply_chains.SupplyChain', null=True, on_delete=models.SET_NULL,
        blank=True, verbose_name=_("Default Supplychain Of Member"),
        related_name='default_supplychain_members')

    def __str__(self):
        """Object name in django admin."""
        return f'{self.user.name} - {self.node.name} - \
            {self.type}'

    class Meta:
        unique_together = ('node', 'user')

    def send_invite(self):
        token = None
        user = self.user
        if not user.password or not user.has_usable_password():
            token = ValidationToken.initialize(
                user, acc_constants.ValidationTokenType.INVITE)
        notification_manager = notifications.MemberInviteNotificationManager(
            user=user, action_object=self, token=token)
        notification_manager.send_notification()

    def get_default_sc(self):
        """Method to return default supplychain"""
        def_sc = self.default_supply_chain
        if not def_sc or \
                not self.node.supply_chains.filter(supply_chain=def_sc).exists():
            self.default_supply_chain = \
                self.node.supply_chains.all().first().supply_chain
            self.save()
        return self.default_supply_chain

    def get_notification_pref(self, notif_manager):
        """
        Function to return notification preferences for a user.
        """
        from v1.notifications.constants import NotificationCondition

        def get_pref(config: dict) -> bool:
            if self.type not in config.keys():
                raise ValueError(_("Config not defined."))
            if config[self.type] == NotificationCondition.ENABLED:
                return True
            elif config[self.type] == NotificationCondition.DISABLED:
                return False
            elif config[self.type] == NotificationCondition.IF_USER_ACTIVE:
                return self.user.status == acc_constants.UserStatus.ACTIVE
            return False

        prefs = {
            "visibility": get_pref(notif_manager.visibility),
            "push": get_pref(notif_manager.push),
            "email": get_pref(notif_manager.email),
            "sms": get_pref(notif_manager.sms)
        }
        return prefs
    
    @property
    def name(self):
        """
        Return node member name.
        """
        return self.user.name
    

class Folder(AbstractBaseModel):
    """
    Model to save folders under a node.
    """
    node = models.ForeignKey(
        'nodes.Node', on_delete=models.CASCADE, verbose_name=_('Node'),
        related_name='folders')
    parent_folder = models.ForeignKey(
        'self', on_delete=models.CASCADE, verbose_name=_('Parent Folder'),
        related_name='child_folders',null=True,blank=True)
    name = models.CharField(
        default='', null=True, blank=True, max_length=500, 
        verbose_name=_('Folder Name'))
    is_deleted = models.BooleanField(
        default=False, verbose_name=_('Is Folder Deleted'))
    
    class Meta:
        """
        Meta info.
        """
        unique_together = ('node','parent_folder','name',)
    
    def __str__(self):
        """Object name in django admin."""
        return f'{self.name} - {self.idencode}'


class NodeDocument(AbstractBaseModel):
    """
    Table to save documents of nodes.

    Atribs:
        node(obj)    : node which the member is related.
        name(str): name of the file
        description(str): description about the document.
        file(file): file.
        is_deleted(bool) : Check to move a file into deleted files section.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    node = models.ForeignKey(
        'nodes.Node', on_delete=models.CASCADE, verbose_name=_('Node'),
        related_name='documents')
    category = models.ForeignKey(
        'tenants.Category', on_delete=models.SET_NULL,
        verbose_name=_('Document Category'), related_name='nodes', null=True,
        blank=True)
    folder = models.ForeignKey(
        Folder, on_delete=models.SET_NULL, verbose_name=_('Folder'),
        related_name='documents',null=True,blank=True)
    tags = models.ManyToManyField(
        'tenants.Tag', related_name='node_documents',
        verbose_name=_('Node Document Tags'))
    
    name = models.CharField(
        default='', null=True, blank=True, max_length=500, 
        verbose_name=_('File Name'))
    description = models.TextField(
        default='', null=True, blank=True, 
        verbose_name=_('File Description'))
    file = models.FileField(
        upload_to=_get_file_path, default=None, max_length=500,
        verbose_name=_('Document'))
    is_deleted = models.BooleanField(
        default=False, verbose_name=_('Is File Deleted'))
    synced_to = models.IntegerField(
        default=None,
        choices=node_consts.DataSyncServers.choices,
        verbose_name=_('Document Synced To'),null=True,blank=True)
    expiry_date = models.DateField(
        null=True, blank=True, default=None, verbose_name=_('Expiry Date'))
    openai_file_id = models.CharField(
        default="", null=True, blank=True, max_length=200,
        verbose_name=_('Open AI File ID'))

    @property
    def file_url(self):
        """Get file url name."""
        try:
            return self.file.url
        except:
            None

    def __str__(self):
        """Object name in django admin."""
        return f'{self.name} - {self.idencode}'

    def notify(self):
        """Notify the node members."""
        for user in self.node.members.all():
            notification_manager = notifications.NodeDocumentNotificationManager(
                user=user, action_object=self, token=None)
            notification_manager.send_notification()
        return True
    
    def file_size(self):
        """
        Return file size.
        """
        try:
            return round(self.file.size / (1024 * 1024),4)
        except:
            return 0.0

    def upload_to_open_ai(self):
        from v1.questionnaire.openai.file_upload import upload_file
        self.openai_file_id = upload_file(self.file)
        self.save()
        return True
