"""Models of the app Products."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Q

import datetime

from base.models import AbstractBaseModel, NumberedModel
from common.library import _get_file_path
from base import session

from v1.nodes.constants import NodeMemberType

from v1.transactions import models as txn_models
from v1.transactions import constants as txn_consts

from v1.risk import constants as risk_consts


class Unit(AbstractBaseModel):
    """
    Model to save units used by each tenant.

    Attribs:
        tenant(obj)     : tenant who holds the unit.
        name(char)      : unit name.
        factor(float)   : common factor value.
        active(bool)    : is the unit still active or not.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
        equivalent_kg(float) : Unit equivalent quantity in kilogram.
    """
    name = models.CharField(
        max_length=500, default='', null=True, 
        blank=True, verbose_name=_('Unit'))
    code = models.CharField(
        max_length=500, default='', null=True, 
        blank=True, verbose_name=_('Unit Symbol'))
    factor = models.FloatField(
        default=0.0, null=True, blank=True, verbose_name=_('Factor Value'))
    is_active = models.BooleanField(default=False, verbose_name=_('Active'))
    equivalent_kg = models.FloatField(
        default=0.0, null=True, blank=True, 
        verbose_name=_('Unit Equivalent In Kilogram'))

    def __str__(self):
        """Function to return value in django admin."""
        return f'{self.name} - {self.idencode}'
    

class ProductType(AbstractBaseModel):
    """
    Model to store common product type of products.
    Like if we consider tata-nano as a product then car is the product type.

    Attribs:
        tenant(obj)       : tenant who holds the supplychain.
        supply_chain(obj) : supplychain of the product.
        product_form(obj) : product_type specific product form.
        batch_form(obj)   : product_type specific batch form.
        name(char)        : supplychain name.
        image(image)      : photo of the supplychain.
        description(char) : description about the supplychain.
        active(bool)      : is the supplychain is active or not.
    """
    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE,
        related_name='product_types', verbose_name=_('Tenant'))
    supply_chain = models.ForeignKey(
        'supply_chains.SupplyChain', on_delete=models.CASCADE,
        related_name='product_types', verbose_name=_('Supplychain'))
    product_form = models.ForeignKey(
        'dynamic_forms.Form', on_delete=models.SET_NULL,
        related_name='product_type_form', verbose_name=_('Product Form'),
        null=True, blank=True)
    batch_form = models.ForeignKey(
        'dynamic_forms.Form', on_delete=models.SET_NULL,
        related_name='product_type_batch_form', verbose_name=_('Batch Form'),
        null=True, blank=True)
    internal_batch_form = models.ForeignKey(
        'dynamic_forms.Form', on_delete=models.SET_NULL,
        related_name='internal_batch_form', verbose_name=_('Internal Batch Form'),
        null=True, blank=True)
    name = models.CharField(
        max_length=500, default='', null=True, 
        blank=True, verbose_name=_('Product Type'))
    image = models.ImageField(
        upload_to=_get_file_path,
        null=True, default=None, blank=True, verbose_name=_('Photo'))
    description = models.CharField(
        max_length=1000, default='', null=True, 
        blank=True, verbose_name=_('Description'))
    is_active = models.BooleanField(default=False, verbose_name=_('Active'))

    def __str__(self):
        """Function to return value in django admin."""
        return f'{self.name} - {self.supply_chain.name} - {self.tenant.name}'


class Product(AbstractBaseModel):
    """
    Model to save products under tenants.

    Attribs:
        tenant(obj)       : tenant who holds the supplychain.
        name(char)        : supplychain name.
        image(image)      : photo of the supplychain.
        description(char) : description about the supplychain.
        unit(obj)         : unit of the product.
        active(bool)      : is the supplychain is active or not.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE,
        related_name='products', verbose_name=_('Tenant'))
    supply_chain = models.ForeignKey(
        'supply_chains.SupplyChain', on_delete=models.CASCADE,
        related_name='products', verbose_name=_('Supplychain'))
    product_type = models.ForeignKey(
        ProductType, on_delete=models.CASCADE,
        related_name='products', verbose_name=_('Product Type'), 
        null=True, blank=True)
    product_specific_form = models.ForeignKey(
        'dynamic_forms.FormSubmission', on_delete=models.SET_NULL,
        related_name='product', verbose_name=_('Product Type Form Data'),
        null=True, blank=True)
    name = models.CharField(
        max_length=500, default='', null=True, 
        blank=True, verbose_name=_('Product'))
    image = models.ImageField(
        upload_to=_get_file_path,
        null=True, default=None, blank=True, verbose_name=_('Photo'))
    description = models.CharField(
        max_length=1000, default='', null=True, 
        blank=True, verbose_name=_('Description'))
    unit = models.ForeignKey(
        'products.Unit', on_delete=models.SET_NULL,
        related_name='products', verbose_name=_('Unit'), null=True)
    is_active = models.BooleanField(default=False, verbose_name=_('Active'))
    is_processed = models.BooleanField(
        default=False, verbose_name=_('Is Processed Product'))
    is_raw = models.BooleanField(
        default=False, verbose_name=_('Is Raw Product'))

    def __str__(self):
        """Function to return value in django admin."""
        return f'{self.name} - {self.supply_chain.name} - {self.tenant.name}'
    
    @property
    def quantity(self):
        """Return available quantity of product under a node/tenant"""
        batches = self.batches.filter(
            Q(incoming_transactions__status=txn_consts.TransactionStatus.APPROVED)|Q(
                incoming_transactions=None))
        node = session.get_current_node()
        if node:
            batches = batches.filter(node=node)
        return batches.aggregate(total=Sum('current_quantity'))['total']


class Batch(AbstractBaseModel, NumberedModel):
    """
    Model to save batches.

    Attribs:
        tenant(obj)                 : tenant who holds the batch.
        product(obj)                : Batch product.
        unit(obj)                   : unit of the product.
        name(char)                  : batch name.
        verified_percentage(float)  : verified product percentage in the 
            batch.
        initial_quantity(float)    : initial quantity of the batch.
        current_quantity(float)    : current quantity of the batch.
        note(char)                 : notes about the batch.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE,
        related_name='batches', verbose_name=_('Tenant'))
    node = models.ForeignKey(
        'nodes.Node', on_delete=models.CASCADE, 
        related_name='batches', null=True,
        verbose_name=_('Node'), blank=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='batches', verbose_name=_('Product'))
    unit = models.ForeignKey(
        Unit, on_delete=models.SET_NULL,
        related_name='batches', verbose_name=_('Unit'), null=True)
    batch_specific_form = models.ForeignKey(
        'dynamic_forms.FormSubmission', on_delete=models.SET_NULL,
        related_name='batch', verbose_name=_('Batch Specific Form Data'),
        null=True, blank=True)
    internal_form_submission = models.ForeignKey(
        'dynamic_forms.FormSubmission', on_delete=models.SET_NULL,
        related_name='linked_batch', 
        verbose_name=_('Internal Batch Specific Form Data'),
        null=True, blank=True)
    name = models.CharField(
        max_length=500, default='', null=True, 
        blank=True, verbose_name=_('Batch'))
    verified_percentage = models.FloatField(
        default=0.0, verbose_name=_('Verified Batch Percentage'))
    initial_quantity = models.DecimalField(
        default=0.0, max_digits=25, decimal_places=3, 
        verbose_name=_('Batch Initial Quantity'))
    initial_quantity_kg = models.DecimalField(
        default=0.0, max_digits=25, decimal_places=3, 
        verbose_name=_('Batch Initial Quantity In KG'))
    current_quantity = models.DecimalField(
        default=0.0, max_digits=25, decimal_places=3, 
        verbose_name=_('Batch Current Quantity'))
    current_quantity_kg = models.DecimalField(
        default=0.0, max_digits=25, decimal_places=3, 
        verbose_name=_('Batch Current Quantity In KG'))
    note = models.CharField(
        max_length=1000, default='', null=True, blank=True, 
        verbose_name=_('Note'))
    risk_score = models.FloatField(default=0.0)
    date = models.DateField(
        default=datetime.date.today, verbose_name=_('Batch Date'))

    def __str__(self):
        """Function to return value in django admin."""
        return f'{self.name}'
    
    def save(self, *args, **kwargs):
        """
        Over riding save method to update transaction number.
        Transaction number is always the django id + 1200
        """
        self.initial_quantity_kg = float(
            self.initial_quantity) * self.unit.equivalent_kg
        self.current_quantity_kg = float(
            self.current_quantity) * self.unit.equivalent_kg
        super(Batch, self).save(*args, **kwargs)

    def transaction_info(self):
        """
        Method returns each type transactions info.
        """
        internal_txns = txn_models.InternalTransaction.objects.filter(
            source_batches=self)
        external_txns = txn_models.ExternalTransaction.objects.filter(
            source_batches=self)
        transaction_info = []
        for int_status in txn_consts.InternalTransactionType.choices:
            type_data = {
                "type_name": int_status[1]
            }
            type_data['quantity'] = float(internal_txns.filter(
                type=int_status[0]).aggregate(quantity=Sum(
                    'source_batch_objects__quantity'))['quantity']or 0.0)
            transaction_info.append(type_data)
        for ext_status in txn_consts.ExternalTransactionType.choices:
            type_data = {
                "type_name": ext_status[1]
            }
            type_data['quantity'] = float(external_txns.filter(
                type=ext_status[0]).aggregate(quantity=Sum(
                    'source_batch_objects__quantity'))['quantity'] or 0.0)
            transaction_info.append(type_data)
        return transaction_info

    def get_claims(self):
        claims = self.batch_claims.all()
        return claims

    @property
    def initial_quantity_in_gram(self):
        """
        Returns batch's initial quantity in grams.
        """
        return self.initial_quantity_kg * 1000

    def extra_info(self):
        """
        Extra info related to logged-in user and the batch.It also shows 
        whether the stock is created or not
        """
        info = {
            'can_add_claim': False,
            'created': True
        }
        member_types = [
            NodeMemberType.ADMIN, 
            NodeMemberType.SUPER_ADMIN, 
            NodeMemberType.TRANSACTION_MANAGER
        ]
        member = session.get_current_node().node_members.get(
            user=session.get_current_user())
        if member.type in member_types or self.current_quantity > 0:
            info['can_add_claim'] = True
        if self.incoming_transactions.first():
            info['created'] = False
        return info

    def tracker_link(self):
        """
        Method returns tracker link of this batch.
        """
        try:
            if not self.incoming_transactions.all().exists():
                return ""
            theme = self.tracker_theme.all().first()
            if not theme:
                theme = self.node.get_tracker_theme()
            batch = self.idencode
            tenant = self.tenant.idencode
            language = self.node.country.language
            return f'tracker/{theme.name}'\
                    f'?batch={batch}&tenant={tenant}&language={language}'
        except:
            return ""

    def source_batches_for_tracker(self):
        """
        Return source batches for tracker by getting the transaction.
        """
        txn = self.incoming_transactions.first()
        if txn.transaction_type == txn_consts.TransactionType.EXTERNAL and (
            txn.child_transaction.type == txn_consts.ExternalTransactionType.REVERSAL or 
            txn.status == txn_consts.TransactionStatus.DECLINED):
            batch = txn.source_batches.first()
            return batch.source_batches_for_tracker()
        else:
            return txn.source_batch_objects.all()
        
    def get_batch_specific_form_id(self):
        """
        Return batch specific form id.
        """
        try:
            return self.batch_specific_form.idencode
        except:
            return None
        
    
    def get_internal_form_submission_id(self):
        """
        Return batch specific form id.
        """
        try:
            return self.internal_form_submission.idencode
        except:
            return None
        
    @property
    def is_available(self):
        """
        Return True if the quantity of the batch is grater than zero.
        """
        return self.current_quantity > 0.0
    
    def risk_score_level(self):
        """
        Return level of risk score.
        """
        if self.risk_score <= 43:
            return risk_consts.Severity.HIGH
        if self.risk_score <= 60:
            return risk_consts.Severity.MEDIUM
        return risk_consts.Severity.LOW
    
    @property
    def province(self):
        """
        Return batch location.
        """
        province = ''
        if self.node:
            province = self.node.province.name
        return province
