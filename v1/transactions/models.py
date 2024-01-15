"""Models of the app Transactions."""

import json
import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.core.validators import validate_comma_separated_integer_list

from base.models import AbstractBaseModel, NumberedModel
from base import session
from base import exceptions
from utilities import functions as util_functions
from common.library import _get_file_path

from v1.transactions import constants as trans_consts
from v1.transactions import notifications

from v1.products import models as prod_models

from v1.blockchain.models.submit_message import AbstractConsensusMessage

from v1.nodes.constants import NodeMemberType


class Transaction(AbstractBaseModel, NumberedModel, AbstractConsensusMessage):
    """
    Base Model for all transactions
    Attributes:
        parents(objs)           : Manytomany fields to map the parent
                                  transactions and thereby the graph of all
                                  transactions.
        date(date)              : The date on which the physical transaction
                                  took place, outside the platform
        transaction_type(int)   : Type of transaction (External/Internal)
        status(int)             : Status of transaction.
        source_quantity(decimal) : Quantity used for the transaction.
        destination_quantity(decimal) : Destination quantity of the 
            transaction.
        source_batches(objs)    : Batches from which the transaction was created.
                                  Automatically created when creating,
                                  SourceBatch
        result_batch(obj)       : The batch that was created after the transaction.

        upload_timestamp               : Offline sync id

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """
    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE, related_name='transactions',
        verbose_name=_('Tenant'))
    parents = models.ManyToManyField(
        'self', related_name='previous_transactions', symmetrical=False,
        blank=True, verbose_name=_('Parent Transactions'))
    date = models.DateField(
        default=datetime.date.today, verbose_name=_('Transaction Date'))
    transaction_type = models.IntegerField(
        default=trans_consts.TransactionType.EXTERNAL,
        choices=trans_consts.TransactionType.choices, 
        verbose_name=_('Type Of Transaction'))
    status = models.IntegerField(
        default=trans_consts.TransactionStatus.CREATED,
        choices=trans_consts.TransactionStatus.choices, 
        verbose_name=_('Status Of Transaction'))
    source_quantity = models.DecimalField(
        max_digits=25, decimal_places=3, default=0.0, null=True,
        blank=True, verbose_name=_('Source Product Quantity'))
    source_quantity_kg = models.DecimalField(
        max_digits=25, decimal_places=3, default=0.0, null=True,
        blank=True, verbose_name=_('Source Product Quantity In KG'))
    destination_quantity = models.DecimalField(
        default=0.0, max_digits=25, decimal_places=3, null=True,
        blank=True, verbose_name=_('Destination Product Quantity'))
    destination_quantity_kg = models.DecimalField(
        max_digits=25, decimal_places=3, default=0.0, null=True,
        blank=True, verbose_name=_('Destination Product Quantity In KG'))
    source_batches = models.ManyToManyField(
        'products.Batch', through='SourceBatch',
        related_name='outgoing_transactions', 
        verbose_name=_('Source Batches'))
    result_batches = models.ManyToManyField(
        'products.Batch', related_name='incoming_transactions', 
        verbose_name=_('Transaction Result Batch'))
    submission_form = models.ForeignKey(
        'dynamic_forms.FormSubmission', on_delete=models.SET_NULL,
        verbose_name=_('Extra Form Data'), null=True, blank=True, 
        related_name='transaction')
    submission_form_mongo_id = models.CharField(
        max_length=100, default='', null=True, blank=True, 
        verbose_name=_('Extra Form Data Mongo Submission Id'))
    unit = models.ForeignKey(
        'products.Unit', on_delete=models.SET_NULL, null=True, 
        verbose_name=_('Unit'))
    note = models.CharField(
        max_length=1000, default='', null=True, blank=True, verbose_name=_('Note'))
    purchase_order = models.ForeignKey(
        'transactions.PurchaseOrder', on_delete=models.SET_NULL,
        verbose_name=_('Attached Purchase Order'), null=True, blank=True, 
        related_name='transactions')
    approver = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.SET_NULL,
        related_name='approved_transactions', 
        verbose_name=_('Approver/Rejector'), null=True, blank=True)
    invoice_number = models.CharField(
        max_length=200, default="", null=True, blank=True)
    upload_timestamp = models.CharField(verbose_name=_('Upload Id'), 
        max_length=255, null=True, blank=True)
    rejection_reason = models.CharField(
        max_length=100, default=None, null=True, blank=True, 
        verbose_name=_('Transaction Rejection Reason'), 
        validators=[validate_comma_separated_integer_list])

    def __str__(self):
        """Object name in django admin."""
        return f'{self.idencode}'

    def save(self, *args, **kwargs):
        """
        Override to add quantity in kg, set created_on to 
        corresponding timestamp in upload_timestamp
        """
        self.tenant = self.tenant or session.get_current_tenant()
        self.source_quantity_kg = float(
            self.source_quantity) * self.unit.equivalent_kg
        self.destination_quantity_kg = float(
            self.destination_quantity) * self.unit.equivalent_kg
        if self.upload_timestamp:
            try:
                self.created_on = timezone.make_aware(
                    datetime.datetime.fromtimestamp(
                    int(self.upload_timestamp)))
            except Exception as ex:
                print(ex)
        super(Transaction, self).save(*args, **kwargs)

    def related_nodes(self):
        """Return nodes related to this transaction"""
        nodes = []
        if self.source_batches:
            nodes.append(self.source_batches.first().node)
        if self.result_batches:
            nodes.append(self.result_batches.first().node)
        return nodes

    def result_products(self):
        """
        Returns result batch products of the transaction.
        """
        return prod_models.Product.objects.filter(
            batches__incoming_transactions=self).distinct()

    def source_products(self):
        """
        Returns source batch products of the transaction.
        """
        return prod_models.Product.objects.filter(
            batches__outgoing_transactions=self).distinct()

    def get_claims(self):
        """
        return claims attached with the transaction.
        """
        claims = self.batch_claims.all()
        return claims

    @property
    def topic_id(self):
        return self.tenant.topic_id

    @property
    def message(self):
        return json.dumps(self.claim_object.claim_info(), cls=DjangoJSONEncoder)

    def logged_date(self):
        """Transaction logged date"""
        return self.created_on.date()

    @property
    def supply_chain(self):
        """Return supply chain"""
        return self.result_batches.first().product.supply_chain
    
    def approve(self, note=None):
        """Api to approve txn"""
        if self.status == trans_consts.TransactionStatus.DECLINED:
            raise exceptions.BadRequest(_("Transaction is already rejected"))
        approver = session.get_current_user()
        self.status = trans_consts.TransactionStatus.APPROVED
        self.approver = approver
        if note:
            self.note = note
        self.save()
        return True

    def reject(self, note=None, rejection_reason=None):
        """Api to reject txn"""
        if self.status == trans_consts.TransactionStatus.APPROVED and \
            not self.tenant.transaction_auto_approval:
            raise exceptions.BadRequest(_("Transaction is already approved"))
        rejector = session.get_current_user()
        self.status = trans_consts.TransactionStatus.DECLINED
        self.approver = rejector
        if note:
            self.note = note
        if rejection_reason:
            self.rejection_reason = rejection_reason
        self.save()
        return True

    @property
    def source_node(self):
        """
        Return source transaction.
        """
        try:
            return self.externaltransaction.source
        except:
            return self.internaltransaction.node
        
    @property
    def source_name(self):
        """return source name"""
        source = ''
        if self.source_node:
            source = self.source_node.name
        return source

    @property
    def destination_node(self):
        """
        Return source transaction.
        """
        try:
            return self.externaltransaction.destination
        except:
            return self.internaltransaction.node
    
    @property
    def child_transaction(self):
        """
        Return child transaction.
        """
        try:
            return self.externaltransaction
        except:
            return self.internaltransaction
        
    @property
    def risk_score(self):
        """
        Return risk score of a transaction.
        """
        if self.result_batches.exists():
            return round(self.result_batches.first().risk_score,2)
        return None
    
    @property
    def risk_score_level(self):
        """
        Return risk score level.
        """
        if self.result_batches.exists():
            return self.result_batches.first().risk_score_level
        return None
    

class SourceBatch(AbstractBaseModel):
    """
    Model contains data of how much quantity of items from which
    batch(es) were taken to create the transaction.

    Attributes:
        transaction(obj)    : Transaction created using the batch.
        batch(obj)          : Batch that was used for the transaction.
        quantity(float)     : Quantity used from the batch for the
                              transaction.
        unit(obj)           : Unit of the batch.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.

    """

    transaction = models.ForeignKey(
        Transaction, related_name='source_batch_objects',
        on_delete=models.CASCADE, verbose_name=_('Transaction'), 
        null=True, blank=True)
    unit = models.ForeignKey(
        'products.Unit', on_delete=models.SET_NULL, null=True, 
        verbose_name=_('Unit'))
    batch = models.ForeignKey(
        'products.Batch', on_delete=models.CASCADE,
        related_name='outgoing_transaction_objects', 
        verbose_name=_('Batch'))
    quantity = models.DecimalField(
        default=0.0, max_digits=25, decimal_places=3, 
        verbose_name=_('Quantity'))
    quantity_kg = models.DecimalField(
        default=0.0, max_digits=25, decimal_places=3, 
        verbose_name=_('Quantity In KG'))

    def __str__(self):
        """Object name in django admin."""
        return f'{self.batch.name} - {self.idencode}'

    def save(self, *args, **kwargs):
        """Update quantity in kg with quantity"""
        self.quantity_kg = float(self.quantity) * self.unit.equivalent_kg
        super(SourceBatch, self).save(*args, **kwargs)


class InternalTransaction(Transaction):
    """
    Model for Internal transactions

    Attributes:
        node(obj)           : Node creating the transaction.
        type(int)           : Internal transaction type.
        mode(int)           : Mode of the transaction
            (manually created or system created)
    
    Inherited Attribs:
        parents(objs)           : Manytomany fields to map the parent
                                  transactions and thereby the graph of all
                                  transactions.
        date(date)              : The date on which the physical transaction
                                  took place, outside the platform
        transaction_type(int)   : Type of transaction (External/Internal)
        status(int)             : Status of transaction.
        source_quantity(decimal) : Quantity used for the transaction.
        destination_quantity(decimal) : Destination quantity of the 
            transaction.
        source_batches(objs)    : Batches from which the transaction was created.
                                  Automatically created when creating,
                                  SourceBatch
        result_batch(obj)       : The batch that was created after the transaction.

        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    node = models.ForeignKey(
        'nodes.Node', on_delete=models.CASCADE,
        default=None, related_name='internaltransactions', 
        verbose_name=_('Node'))
    type = models.IntegerField(
        default=trans_consts.InternalTransactionType.PROCESSING,
        choices=trans_consts.InternalTransactionType.choices, 
        verbose_name=_('Type Of Internal Transaction'))
    mode = models.IntegerField(
        default=trans_consts.TransactionMode.MANUAL,
        choices=trans_consts.TransactionMode.choices, 
        verbose_name=_('Mode Of Transaction'))

    def __str__(self):
        """Object name in django admin."""
        return f'{self.node.name} - {self.get_type_display()} - \
            {self.idencode}'
    
    @property
    def name(self):
        """
        Return name for the transaction
        """
        completer = ''
        source_products = list(
            self.source_products().values_list('name', flat=True))
        end_products = list(
            self.result_products().values_list('name', flat=True))
        unit = self.source_batches.first().unit.name
        if self.type == trans_consts.InternalTransactionType.PROCESSING:
            completer = _('converted to {products}').format(products=",".join(end_products))
        elif self.type == trans_consts.InternalTransactionType.MERGE:
            unit = self.result_batches.first().unit.name
            completer = _('merged')
        else:
            unit = self.source_batches.first().unit.name
            completer = _('removed')
        name = _('{quantity} {unit} {products} {completer}'.format(
            # kg_quantity=formats.localize(self.source_quantity_kg, use_l10n=True),
            quantity=self.source_quantity, 
            unit=unit,
            products=",".join(source_products),
            completer=completer
        ))
        if self.type == trans_consts.InternalTransactionType.PROCESSING:
            name = _('{products} {completer}'.format(
            products=",".join(source_products),
            completer=completer))
        return name

    @property
    def message(self):
        sb_texts = [
            "%s%s of %s" % (
                bat.quantity, bat.unit_display,
                bat.batch.product.name)
            for bat in self.source_batch_objects.all()
        ]
        source_batch_info = util_functions.list_to_sentence(sb_texts)
        rb_texts = [
            "%s%s of %s" % (
                bat.initial_quantity,
                bat.unit_display, bat.product.name)
            for bat in self.result_batches.all()
        ]
        result_batch_info = util_functions.list_to_sentence(rb_texts)
        data = {
            'source_batches': source_batch_info,
            'result_batches': result_batch_info
        }
        return json.dumps(data, cls=DjangoJSONEncoder)

    def get_created_by(self):
        """
        Returns a string about the transaction type.
        """
        return _("Created by {action}").format(action=self.get_type_display())


class ExternalTransaction(Transaction):
    """
    Model for External Transactions

    Attributes:
        source(obj)     : Source Node of transaction.
        destination(obj): Destination Node of transaction.
        price(float)     : Price paid for transaction.
        currency        : Currency of payment.
        type            : Type of transaction incoming/outgoing.

    Inherited Attribs:
        parents(objs)           : Manytomany fields to map the parent
                                  transactions and thereby the graph of all
                                  transactions.
        date(date)              : The date on which the physical transaction
                                  took place, outside the platform
        transaction_type(int)   : Type of transaction (External/Internal)
        status(int)             : Status of transaction.
        source_quantity(decimal) : Quantity used for the transaction.
        destination_quantity(decimal) : Destination quantity of the 
            transaction.
        source_batches(objs)    : Batches from which the transaction was created.
                                  Automatically created when creating,
                                  SourceBatch
        result_batch(obj)       : The batch that was created after the transaction.

        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    source = models.ForeignKey(
        'nodes.Node', on_delete=models.CASCADE,
        related_name='outgoing_transactions', 
        verbose_name=_('Source Node'), null=True, blank=True)
    destination = models.ForeignKey(
        'nodes.Node', on_delete=models.CASCADE,
        related_name='incoming_transactions', 
        verbose_name=_('Destination Node'))
    price = models.FloatField(
        default=None, null=True, blank=True, verbose_name=_('Price'))
    currency = models.ForeignKey(
        'tenants.Currency', on_delete=models.CASCADE,
        related_name='external_transactions', 
        verbose_name=_('Currency'), null=True, blank=True)
    type = models.IntegerField(
        default=trans_consts.ExternalTransactionType.INCOMING,
        choices=trans_consts.ExternalTransactionType.choices, 
        verbose_name=_('Type Of External Transaction'))

    def __str__(self):
        """Object name in django admin."""
        return f'{self.source} - {self.destination.name} - {self.get_type_display()} | {self.idencode}'

    @property
    def name(self, is_source=False):
        """
        Return name for the transaction
        """
        is_source = (session.get_current_node() == self.source)
        name = ""
        if is_source and self.type != trans_consts.ExternalTransactionType.REVERSAL:
            name = _("{quantity} {unit} {product_name} send to {name}").format(
                # kg_quantity=formats.localize(self.source_quantity_kg, use_l10n=True),
                quantity=self.destination_quantity,
                unit=self.result_batch.unit.name,
                product_name=self.source_batches.first().product.name,
                name=self.destination.name)
        elif self.type == trans_consts.ExternalTransactionType.INCOMING_WITHOUT_SOURCE:
            name = _("{quantity} {unit} {product_name} received.").format(
                # kg_quantity=formats.localize(self.destination_quantity_kg, use_l10n=True),
                quantity=self.destination_quantity,
                unit=self.result_batch.unit.name,
                product_name=self.source_batches.first().product.name)
        elif self.type != trans_consts.ExternalTransactionType.REVERSAL:
            name = _("{quantity} {unit} {product_name} received from {name}.").format(
                # kg_quantity=formats.localize(self.destination_quantity_kg, use_l10n=True),
                product_name=self.source_batches.first().product.name,
                quantity=self.destination_quantity,
                unit=self.result_batch.unit.name,
                name=self.source.name)
        elif is_source:
            name = _("{quantity} {unit} {product_name} sent back to {name}.").format(
                # kg_quantity=formats.localize(self.source_quantity_kg, use_l10n=True),
                quantity=self.destination_quantity,
                unit=self.result_batch.unit.name,
                product_name=self.source_batches.first().product.name,
                name=self.destination.name)
        else:
            name = _("{quantity} {unit} {product_name} sent back to {name}.").format(
                # kg_quantity=formats.localize(self.source_quantity_kg, use_l10n=True),
                quantity=self.destination_quantity,
                unit=self.result_batch.unit.name,
                product_name=self.source_batches.first().product.name,
                name=self.destination.name)
        return name

    @property
    def product(self):
        """
        Returns single product created after the txn.
        """
        return self.result_products.first()

    @property
    def result_batch(self):
        """
        Returns single result batch.
        """
        return self.result_batches.first()

    def get_additional_info(self):
        """
        Method returns dict of current txn with important data.
        """
        data = {
            'number': self.number,
            'date': self.date.strftime("%d %B %Y"),
            'product_name': self.product.name,
            'unit': self.result_batch.unit_display,
            'quantity': self.result_batch.initial_quantity_in_gram,
            'supply_chain': self.product.supply_chain.name,
            'sender': self.source_name,
            'receiver': self.destination.name
        }
        return data

    @property
    def message(self):
        return json.dumps(
            self.get_additional_info(), cls=DjangoJSONEncoder)

    def notify(self):
        """Notify target node members that transaction created"""
        if self.type == trans_consts.ExternalTransactionType.OUTGOING:
            target_node = self.destination
            NotificationManager = notifications.TransactionReceivedNotificationManager
        elif self.type == trans_consts.ExternalTransactionType.INCOMING:
            target_node = self.source
            NotificationManager = notifications.TransactionSentNotificationManager
        elif self.type == trans_consts.ExternalTransactionType.REVERSAL:
            target_node = self.destination
            NotificationManager = notifications.TransactionApprovalNotificationManager
        else:
            return False

        for user in target_node.members.all():
            notification_manager = NotificationManager(
                user=user, action_object=self, token=None)
            notification_manager.send_notification()
        return True

    def extra_info(self):
        """
        Method return extra data about the current user can alter the 
        transaction object or not.
        """
        member = session.get_current_user().member_nodes.get(
            node=session.get_current_node())
        info = {
            "can_approve": False, 
            "can_reject": False, 
            "can_add_claim": False
        }
        if member.node == self.source and \
            self.status == trans_consts.TransactionStatus.CREATED:
                info['can_add_claim'] = True
                return info
        if self.type == trans_consts.ExternalTransactionType.OUTGOING and \
            member.node == self.destination:
            exclude_member_types = [
                NodeMemberType.CONNECTION_MANAGER,
                NodeMemberType.REPORTER]
            exclude_txn_statuses = [
                trans_consts.TransactionStatus.APPROVED,
                trans_consts.TransactionStatus.DECLINED]
            if member.type not in exclude_member_types and \
                self.status not in exclude_txn_statuses:
                info['can_reject'] = True
                info['can_approve'] = True
            new_txns = Transaction.objects.filter(
                source_batches__in=self.result_batches.all())
            if session.get_current_tenant().transaction_auto_approval and (
                    not new_txns.exists()):
                info['can_reject'] = True
        return info


class PurchaseOrder(AbstractBaseModel, NumberedModel):
    """
    Model to store purchase orders from node and product delivering queries 
    of node.

    Attributes:
        sender(obj)     : Enquiry sender.
        receiver(obj)   : Enquiry receiver.
        price(float)    : Purchase order expected price.
        currency(char)  : Currency.
        product(obj)    : Product needed.
        quantity(decimal): Quantity of the product needed.
        unit(obj)       : Unit of the expected quantity.
        status(int)     : Status of the enquiry.
        type(int)       : Purchase order or sender enquiry.
        claims(objs)    : Claims required for the product.
        expected_date(date): Expected product delivery date.
        date(date)      : Enquiry date.
        last_noti_date(date): Last notification send date.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    sender = models.ForeignKey(
        'nodes.Node', on_delete=models.CASCADE,
        related_name='created_enquiries', verbose_name=_('Sender'))
    receiver = models.ForeignKey(
        'nodes.Node', on_delete=models.CASCADE,
        related_name='received_enquiries', verbose_name=_('Receiver'))
    price = models.FloatField(
        default=None, null=True, blank=True, verbose_name=_('Price'))
    currency = models.ForeignKey(
        'tenants.Currency', on_delete=models.CASCADE,
        related_name='txn_enquiries', 
        verbose_name=_('Currency'), null=True, blank=True)
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        related_name='transaction_enquiries', verbose_name=_('Product'))
    quantity = models.DecimalField(
        default=0.0, max_digits=25, decimal_places=3, 
        verbose_name=_('Quantity Of Product'))
    quantity_kg = models.DecimalField(
        default=0.0, max_digits=25, decimal_places=3, 
        verbose_name=_('Quantity Of Product In KG'))
    sent_quantity = models.DecimalField(
        default=0.0, max_digits=25, decimal_places=3, 
        verbose_name=_('Sent Quantity Of Product'))
    sent_quantity_kg = models.DecimalField(
        default=0.0, max_digits=25, decimal_places=3, 
        verbose_name=_('Sent Quantity Of Product In KG'))
    unit = models.ForeignKey(
        'products.Unit', on_delete=models.SET_NULL, null=True, 
        verbose_name=_('Unit Of Product'))
    status = models.IntegerField(
        default=trans_consts.PurchaseOrderStatus.PENDING,
        choices=trans_consts.PurchaseOrderStatus.choices, 
        verbose_name=_('PurachaseOrder Status'))
    claims = models.ManyToManyField(
        'claims.Claim', related_name='requested_enquiries', 
        verbose_name=_('Claims Needed'))
    expected_date = models.DateField(
        default=datetime.date.today, 
        verbose_name=_('Expected Delivery Date'))
    date = models.DateField(
        default=datetime.date.today, verbose_name=_('Enquiry Date'))
    last_noti_date = models.DateTimeField(
        default=datetime.datetime.today, 
        verbose_name=_('Last Notification Date'))
    submission_form = models.ForeignKey(
        'dynamic_forms.FormSubmission', on_delete=models.SET_NULL,
        verbose_name=_('Extra Form Data'), null=True, blank=True, 
        related_name='transaction_enquiry')
    submission_form_mongo_id = models.CharField(
        max_length=100, default='', null=True, blank=True, 
        verbose_name=_('Extra Form Data Mongo Submission Id'))
    comment = models.TextField(
        default='', null=True, blank=True, verbose_name=_('Comment'))
    rejection_note = models.TextField(
        default='', null=True, blank=True, verbose_name=_('Rejection Reason'))

    def __str__(self):
        """Object name in django admin."""
        return f'{self.sender.name} - {self.receiver.name} - {self.idencode}'

    def save(self, *args, **kwargs):
        """Update quantity in kg with quantity"""
        self.quantity_kg = float(self.quantity) * self.unit.equivalent_kg
        self.sent_quantity_kg = float(
            self.sent_quantity) * self.unit.equivalent_kg
        super(PurchaseOrder, self).save(*args, **kwargs)

    def is_modifiable(self):
        """
        Method returns the po is modifiable or not.
        """
        if self.status == trans_consts.PurchaseOrderStatus.PENDING:
            return True
        return False

    def reject(self, response=None):
        """
        Method used to reject po.
        Checks purchase order's current status before rejecting and sends
        notification after rejection.
        (Response aka rejection reason is taken as parameter.)
        """
        if not self.status == trans_consts.PurchaseOrderStatus.APPROVED:
            self.rejection_note = response
            self.status = trans_consts.PurchaseOrderStatus.REJECTED
            self.save()
            self.notify_po_approval()
            return True
        return False

    def remove(self):
        """
        Method used to remove po.
        Checks purchase order's current status before removing and sends
        notification after removal.
        """
        if not self.status == trans_consts.PurchaseOrderStatus.APPROVED:
            self.status = trans_consts.PurchaseOrderStatus.CANCELLED
            self.save()
            self.notify_po_approval()
            return True
        return False

    def approve(self):
        """
        Method used to approve po.
        Checks purchase order's current status before approving and sends
        notification after approval.
        """
        if self.status in [
            trans_consts.PurchaseOrderStatus.PARTIAL, 
            trans_consts.PurchaseOrderStatus.PENDING, 
            trans_consts.PurchaseOrderStatus.ON_HOLD]:
            self.status = trans_consts.PurchaseOrderStatus.APPROVED
            self.save()
            self.notify_po_approval()
            return True
        return False

    @property
    def remaining_quantity(self):
        """return remaining quantity to send"""
        return float(self.quantity) - float(self.sent_quantity)

    def notify(self, update=False):
        """Notifies purchase order creation"""
        if update:
            NotificatioManager = notifications.PurchaseOrderUpdateNotificationManager
        else:
            NotificatioManager = notifications.PurchaseOrderCreatedNotificationManager

        for user in self.receiver.members.all():
            notification_manager = NotificatioManager(
                user=user, action_object=self, token=None)
            notification_manager.send_notification()
        return True

    def notify_po_approval(self):
        """Notifies purchase order approval."""
        node = self.sender
        if self.status == trans_consts.PurchaseOrderStatus.CANCELLED:
            node = self.receiver
        for user in node.members.all():
            notification_manager = notifications.PurchaseOrderApprovalNotificationManager(
                user=user, action_object=self, token=None)
            notification_manager.send_notification()
        return True

    def extra_info(self):
        """Extra info related to user and purchase-order"""
        info = {
            'can_reject': False, 
            'can_send_stock': False, 
            'can_edit': False, 
            'can_remove': False
        }
        member_types = [
            NodeMemberType.ADMIN, 
            NodeMemberType.SUPER_ADMIN, 
            NodeMemberType.TRANSACTION_MANAGER
            ]
        member = session.get_current_node().node_members.get(
            user=session.get_current_user())
        if self.status != trans_consts.PurchaseOrderStatus.PENDING and \
            self.status != trans_consts.PurchaseOrderStatus.PARTIAL:
            return info
        if member.type in member_types:
            if self.sent_quantity <= 0:
                if member.node == self.sender:
                    info['can_remove'] = True
                    info['can_edit'] = True
                if member.node == self.receiver:
                    info['can_reject'] = True
            if self.sent_quantity < self.quantity and \
                member.node == self.receiver:
                info['can_send_stock'] = True
        return info


class TransactionComment(AbstractBaseModel):
    """
    Model to save comments related to a transaction 
    which incudes text nd document.
    """

    transaction = models.ForeignKey(
        Transaction, related_name='comments',
        on_delete=models.CASCADE, verbose_name=_('Transaction'))
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
        related_name='txn_comments', verbose_name=_('Commenter'))
    company_document = models.ForeignKey('nodes.NodeDocument', 
        on_delete=models.CASCADE, null=True, blank=True, 
        related_name='trans_document')

    def __str__(self) -> str:
        """Object name in django admin."""
        return f'{self.transaction} - {self.name} - {self.idencode}'

    @property
    def file_url(self):
        """Get file url name."""
        try:
            return self.file.url
        except:
            None

    def extra_info(self):
        """
        Method return extra data about the current user can alter the 
        transaction object or not.
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
        """Notify all the members related to the transaction."""
        source_node = self.transaction.source_node
        destination_node = self.transaction.destination_node
        if source_node:
            for member in source_node.node_members.exclude(id=self.member.id):
                notification_manager = notifications.TransactionCommentNotificationManager(
                    user=member.user, action_object=self, token=None)
                notification_manager.send_notification()
        if source_node != destination_node:
            for member in destination_node.node_members.exclude(id=self.member.id):
                notification_manager = notifications.TransactionCommentNotificationManager(
                    user=member.user, action_object=self, token=None)
                notification_manager.send_notification()
        return True


class DeliveryNotification(AbstractBaseModel):
    """
    Model to save delivery information related to a purchase order.
   """

    purchase_order = models.ForeignKey(
        PurchaseOrder, related_name='delivery_notification',
        on_delete=models.CASCADE, verbose_name=_('PurchaseOrder'))
    quantity = models.DecimalField(
        default=0.0, max_digits=25, decimal_places=3,
        verbose_name=_('Quantity Of Product'))
    expected_date = models.DateField(
        default=datetime.date.today,
        verbose_name=_('Expected Delivery Date'))
    comment = models.TextField(
        default='', null=True, blank=True, verbose_name=_('Comment'))

    def __str__(self) -> str:
        """Object name in django admin."""
        return f'{self.purchase_order} - {self.idencode}'

    def notify(self):
        """Notify all the members of batch reciever of the purchase order."""
        for user in self.purchase_order.sender.members.all():
            notification_manager = notifications.DeliveryNotificationManager(
                user=user, action_object=self, token=None)
            notification_manager.send_notification()
        return True
