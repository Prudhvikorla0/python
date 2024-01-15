"""Models of the app Supplychains."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from positions import PositionField

from base.models import AbstractBaseModel, NumberedModel
from common.library import _get_file_path

from v1.accounts.models import ValidationToken
from v1.accounts import constants as acc_constants

from v1.nodes import constants as node_consts

from v1.supply_chains import constants as sc_constants
from v1.supply_chains import notifications
from v1.supply_chains import graph_models as sc_graph_models

from v1.risk import constants as risk_consts


class Operation(AbstractBaseModel):
    """
    Available operations for a Node

    Attributes:
        node_type(int[choice])  : Type of the Node (Company of Producer)
        name(str)               : Operation name
        image(image)            : Default image for the operation
    """

    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE,
        related_name='node_operations', verbose_name=_('Tenant'))
    node_type = models.IntegerField(
        choices=node_consts.NodeType.choices, 
        default=node_consts.NodeType.COMPANY, 
        verbose_name=_('Type Of Node'))
    name = models.CharField(
        max_length=100, default='', verbose_name=_('Category'))
    image = models.FileField(
        upload_to=_get_file_path, blank=True, verbose_name=_('Photo'))
    invitation_form = models.ForeignKey(
        'dynamic_forms.Form', on_delete=models.SET_NULL, null=True,
        blank=True, verbose_name=_('Extra Fields For Invitation'),
        related_name='invitation_form_operation')
    signup_form = models.ForeignKey(
        'dynamic_forms.Form', on_delete=models.SET_NULL, null=True,
        blank=True, verbose_name=_('Extra Fields For Signup'),
        related_name='signup_form_operation')
    in_dashboard = models.BooleanField(
        default=True, verbose_name=_('Dashboard_visible'))
    in_forms = models.BooleanField(
        default=True, verbose_name=_('Form_visible'))
    position = PositionField(
        collection='tenant', default=1,
        verbose_name=_('Operation Position'))

    def __str__(self):
        """Object name in django admin."""
        return f'{self.name} - {self.node_type} - {self.tenant.name}'

    class Meta:
        unique_together = ('tenant', 'node_type', 'name')


class SupplyChain(AbstractBaseModel):
    """
    Model to save supllychains used under a tenant.

    Attribs:
        tenant(obj)       : tenant who holds the supplychain.
        name(char)        : supplychain name.
        image(image)      : photo of the supplychain.
        description(char) : description about the supplychain.
        active(bool)      : is the supplychain is active or not.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE,
        related_name='supply_chains', verbose_name=_('Tenant'))
    name = models.CharField(
        max_length=500, default='', verbose_name=_('Supply Chain Name'))
    image = models.ImageField(
        upload_to=_get_file_path,
        null=True, default=None, blank=True, verbose_name=_('Photo'))
    description = models.CharField(
        max_length=1000, default='', null=True,
        blank=True, verbose_name=_('Description'))
    is_active = models.BooleanField(default=False, verbose_name=_('Active'))

    def __str__(self):
        """Function to return value in django admin."""
        return f'{self.name} - {self.idencode} - {self.tenant.name}'


class Connection(AbstractBaseModel, NumberedModel):
    """
    Model to save connection between two nodes.

    Atribs:
        tenant(obj)   : Tenant which hold the connection.
        source(obj)   : Connecting node.
        target(obj)   : Connected node.
        graph_id(char): Graph db id.
        status(int)   : Status of the connection.
        supplychain(obj) : Connection holding supplychain.
        source_tags(objs) : Tags about the source node.
        target_tags(objs) : Tags about the target node.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE,
        related_name='connections', verbose_name=_('Tenant'))
    connection_pair = models.OneToOneField(
        'self', on_delete=models.CASCADE, related_name='paired_connections',
        null=True, blank=True, verbose_name=_('Connection pair'))
    initiation = models.IntegerField(
        choices=sc_constants.ConnectionInitiation.choices,
        default=sc_constants.ConnectionInitiation.MANUAL)
    source = models.ForeignKey(
        'nodes.Node', on_delete=models.CASCADE, related_name='source_connections',
        verbose_name=_('Connected From'))
    target = models.ForeignKey(
        'nodes.Node', on_delete=models.CASCADE, related_name='target_connections',
        verbose_name=_('Connected To'))
    supply_chain = models.ForeignKey(
        'supply_chains.SupplyChain', on_delete=models.CASCADE,
        related_name='connections', verbose_name=_('Supplychain'))
    tags = models.ManyToManyField(
        'tenants.Tag', related_name='connections',
        verbose_name=_('Connection Tags'))
    submission_form = models.ForeignKey(
        'dynamic_forms.FormSubmission', on_delete=models.SET_NULL,
        related_name='connection', verbose_name=_('Extra Form Data'),
        null=True, blank=True)
    submission_form_mongo_id = models.CharField(
        max_length=100, default='', null=True, blank=True, 
        verbose_name=_('Extra Form Data Mongo Submission Id'))
    graph_id = models.CharField(
        max_length=200, default='', null=True, blank=True,
        verbose_name=_('GraphDB Id'))
    status = models.IntegerField(
        default=sc_constants.ConnectionStatus.PENDING,
        choices=sc_constants.ConnectionStatus.choices,
        verbose_name=_('Connection Status'))
    invited_by = models.ForeignKey(
        'nodes.Node', on_delete=models.SET_NULL, 
        related_name='created_connections', null=True, 
        blank=True, verbose_name=_('Invited By'))

    is_buyer = models.BooleanField(
        default=True, verbose_name=_('Target is a Buyer'))
    is_supplier = models.BooleanField(
        default=True, verbose_name=_('Target is a Supplier'))

    class Meta:
        unique_together = ('source', 'target', 'supply_chain')

    def __str__(self):
        """Object name in django admin."""
        return f'{self.source.name} -> {self.target.name} | {self.idencode}'

    def send_invite(self):
        """Function to set password."""
        for user in self.target.members.all():
            token = None
            if not user.password or not user.has_usable_password():
                token = ValidationToken.initialize(
                    user, acc_constants.ValidationTokenType.INVITE)
            notification_manager = notifications.NodeInviteNotificationManager(
                user=user, action_object=self, token=token)
            notification_manager.send_notification()
        return True
    
    @property
    def name(self):
        """
        Method returns connection name
        """
        return f"{self.source.name} -> {self.target.name}"
    
    def update_graphdb(self):
        """
        """
        target_node_sc = NodeSupplyChain.objects.get(
            node=self.target, 
            supply_chain=self.supply_chain)
        try:
            target_connection = sc_graph_models.NodeGraphModel.nodes.first(
                pg_node_id=self.target.id,pg_node_idencode=self.target.idencode,
                pg_node_sc_id=target_node_sc.id,
                pg_node_sc_idencode=target_node_sc.idencode,
                type=self.target.type,full_name=self.target.name
            )
        except:
            target_connection = sc_graph_models.NodeGraphModel(
            pg_node_id=self.target.id,pg_node_idencode=self.target.idencode,
            pg_node_sc_id=target_node_sc.id,
            pg_node_sc_idencode=target_node_sc.idencode,
            type=self.target.type,full_name=self.target.name
            )
        source_node_sc = NodeSupplyChain.objects.get(
            node=self.source, 
            supply_chain=self.supply_chain)
        try:
            source_connection = sc_graph_models.NodeGraphModel.nodes.first(
                pg_node_id=self.source.id,pg_node_idencode=self.source.idencode,
                pg_node_sc_id=source_node_sc.id,
                pg_node_sc_idencode=source_node_sc.idencode,
                type=self.source.type,full_name=self.source.name
            )
        except:
            source_connection = sc_graph_models.NodeGraphModel(
            pg_node_id=self.source.id,pg_node_idencode=self.source.idencode,
            pg_node_sc_id=source_node_sc.id,
            pg_node_sc_idencode=source_node_sc.idencode,
            type=self.source.type,full_name=self.source.name
            )
        target_connection.save()
        source_connection.save()
        if self.is_supplier:
            target_connection.suppliers.connect(
                source_connection, {"supply_chain_id": self.supply_chain.id})
        if self.is_buyer:
            target_connection.buyers.connect(
                source_connection, {"supply_chain_id": self.supply_chain.id})
        return True
    
    def get_target_node_sc(self):
        """
        Returns target node's supplychain model.
        """
        node_sc = self.target.supply_chains.get(
            supply_chain=self.supply_chain)
        return node_sc
    
    def sc_risk_score(self):
        """
        Return target node's sc risk score.
        """
        return round(self.get_target_node_sc().sc_risk_score,2)
    
    def sc_risk_level(self):
        """
        Return target node's sc risk score.
        """
        return self.get_target_node_sc().sc_risk_level


class NodeSupplyChain(AbstractBaseModel):
    """
    Model to store supplychains of node.
    """

    supply_chain = models.ForeignKey(
        SupplyChain, on_delete=models.CASCADE, related_name='node_supplychains',
        verbose_name=_('Supply Chain'))
    node = models.ForeignKey(
        'nodes.Node', on_delete=models.CASCADE, related_name='supply_chains', 
        verbose_name=_('Node'))
    is_active = models.BooleanField(default=True)
    sc_risk_score = models.FloatField(default=0.0)
    sc_risk_updated_on = models.DateTimeField(
        null=True, blank=True,default=timezone.now)

    def __str__(self):
        """Object name in django admin."""
        return f'{self.node.name} - {self.supply_chain.name} | {self.idencode}'
    
    @property
    def sc_risk_level(self):
        if self.sc_risk_score <= 43:
            return risk_consts.Severity.HIGH
        if self.sc_risk_score <= 60:
            return risk_consts.Severity.MEDIUM
        return risk_consts.Severity.LOW

    class Meta:
        """
        Meta Setup.
        """
        unique_together = ('supply_chain', 'node')
