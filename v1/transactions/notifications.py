
from django.utils.translation import gettext_lazy as _
from django.utils import formats

from base import session
from common.library import change_date_format

from v1.nodes.constants import NodeMemberType
from v1.nodes.models import NodeMember
from v1.nodes.constants import NodeMemberType

from v1.notifications.manager import BaseNotificationManager
from v1.notifications.constants import NotificationCondition

from v1.transactions import constants


class TransactionSentNotificationManager(BaseNotificationManager):
    """
    Notification manager for sending email notification and push notifications
    to sender node members that transaction is sent.
    Only for receive transactions
    """

    notification_uid: str = "transaction_sent"

    action_text: str = _("Show Transaction")

    visibility: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.ENABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    push: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    email: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    sms: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.ENABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }

    def get_title(self) -> str:
        return _("{batch_name} sent to {destination_name}.").format(
            batch_name=self.action_object.result_batches.first().product.name,
            destination_name=self.action_object.destination.name,)

    def get_body(self) -> str:
        stock_desc = _("{quantity}{unit} of {product}").format(
            quantity=formats.localize(self.action_object.destination_quantity, use_l10n=True),
            unit=self.action_object.unit.code,
            product=self.action_object.result_batches.first().product.name)

        return _("The sale of {stock_desc} to {destination_name} was completed on {date}. "
                 "You were paid {amount} {currency} for the transaction.").format(
            stock_desc=stock_desc,
            destination_name=self.action_object.destination.name,
            date=self.action_object.date.strftime('%d/%m/%Y'),
            amount=formats.localize(self.action_object.price, use_l10n=True),
            currency=self.action_object.currency.code,
        )

    def get_url_path(self):
        return f"/transactions/transaction-detail/external/{self.action_object.idencode}/"

    def get_actor_node(self):
        return self.action_object.destination

    def get_target_node(self):
        return self.action_object.source

    def get_supply_chain(self):
        return self.action_object.supply_chain

    def get_redirect_id(self):
        return self.action_object.id

    def get_tenant(self):
        return self.action_object.tenant


class TransactionReceivedNotificationManager(BaseNotificationManager):
    """
    Notification manager for sending email notification and push notifications
    to reciever node members that transaction is created.
    """

    notification_uid: str = "transaction_received"

    action_text: str = _("Show Transaction")

    visibility: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.ENABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    push: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    email: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    sms: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.DISABLED,
        NodeMemberType.ADMIN: NotificationCondition.DISABLED,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }

    email_template: str = "default.html"

    def get_title(self) -> str:
        if self.action_object.purchase_order:
            return _("Transaction received from {source_name} for the purchase order {po_num}").format(
                source_name=self.action_object.source.name,
                po_num=self.action_object.purchase_order.number)
        else:
            return _("{batch_name} received from {source_name}.").format(
                batch_name=self.action_object.result_batches.first().product.name,
                source_name=self.action_object.source.name,)

    def get_body(self) -> str:
        stock_desc = _("{kg_quantity}{unit} of {product}").format(
            kg_quantity=formats.localize(self.action_object.destination_quantity, use_l10n=True),
            unit=self.action_object.unit.code,
            product=self.action_object.result_batches.first().product.name)
        if self.action_object.purchase_order:
            return _("{stock_desc} received from {name} for purchase order {po_num}").format(
                stock_desc=stock_desc,
                name=self.action_object.source.name,
                po_num=self.action_object.purchase_order.number)
        else:
            return _("{stock_desc} received from {name}.").format(
                stock_desc=stock_desc,
                name=self.action_object.source.name)

    def get_url_path(self):
        return f"/transactions/transaction-detail/external/{self.action_object.idencode}/"

    def get_actor_node(self):
        return self.action_object.source

    def get_target_node(self):
        return self.action_object.destination

    def get_supply_chain(self):
        return self.action_object.supply_chain

    def get_redirect_id(self):
        return self.action_object.id

    def get_tenant(self):
        return self.action_object.tenant


class TransactionApprovalNotificationManager(BaseNotificationManager):
    """
     Notification manager for sending email notification and push notifications
    to sender node members that transaction is approved / rejected.
    """

    notification_uid: str = "transaction_approval"

    action_text: str = _("Show Transaction")

    visibility: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.ENABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    push: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    email: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    sms: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.DISABLED,
        NodeMemberType.ADMIN: NotificationCondition.DISABLED,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }

    email_template: str = "default.html"

    def get_title(self) -> str:
        if self.action_object.status == constants.TransactionStatus.APPROVED:
            return _("Batch sent to {name} is approved").format(name=self.action_object.destination.name)
        else:
            return _("Batch sent to {name} is rejected and batch reversed.").format(name=self.action_object.destination.name)

    def get_body(self) -> str:
        stock_desc = _("{kg_quantity}{unit} of {product}").format(
            kg_quantity=formats.localize(self.action_object.destination_quantity, use_l10n=True),
            unit=self.action_object.unit.code,
            product=self.action_object.result_batches.first().product.name)
        if self.action_object.status == constants.TransactionStatus.APPROVED:
            return _("{stock_desc} sent to {name} is accepted").format(
                stock_desc=stock_desc, name=self.action_object.destination.name)
        else:
            return _("{stock_desc} sent to {name} is rejected").format(
                stock_desc=stock_desc, name=self.action_object.destination.name)

    def get_url_path(self):
        return f"/transactions/transaction-detail/external/{self.action_object.idencode}/"

    def get_actor_node(self):
        return self.action_object.destination

    def get_target_node(self):
        return self.action_object.source

    def get_supply_chain(self):
        return self.action_object.supply_chain 

    def get_redirect_id(self):
        return self.action_object.id

    def get_tenant(self):
        return self.action_object.tenant


class PurchaseOrderCreatedNotificationManager(BaseNotificationManager):
    """
     Notification manager for sending email notification and push notifications
    to reciever node members that purchase order is created.
    """

    notification_uid: str = "purchase_order_create"

    action_text: str = _("Show Purchase Order")

    visibility: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    push: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    email: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    sms: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.DISABLED,
        NodeMemberType.ADMIN: NotificationCondition.DISABLED,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }

    email_template: str = "default.html"

    def get_title(self) -> str:
        return _("Purchase Order({po_num}) received from {name}").format(
            po_num=self.action_object.number,
            name=self.action_object.sender.name)

    def get_body(self) -> str:
        stock_desc = _("{kg_quantity}{unit} of {product}").format(
            kg_quantity=formats.localize(self.action_object.quantity, use_l10n=True),
            unit=self.action_object.unit.code,
            product=self.action_object.product.name)
        return _("Purchase Order({po_num}) received from {name} for {stock_desc}").format(
            po_num=self.action_object.number,
            name=self.action_object.sender.name,
            stock_desc=stock_desc)

    def get_url_path(self):
        return f"purchase-order/order-details/receive/{self.action_object.idencode}/"
        
    def get_actor_node(self):
        return self.action_object.sender

    def get_target_node(self):
        return self.action_object.receiver

    def get_supply_chain(self):
        return self.action_object.product.supply_chain

    def get_redirect_id(self):
        return self.action_object.id

    def get_redirect_type(self):
        return 'receive'

    def get_tenant(self):
        return self.action_object.sender.tenant


class PurchaseOrderUpdateNotificationManager(BaseNotificationManager):
    """
    Notification manager for sending email notification and push notifications
    to reciever node members that purchase order is updated.
    """

    notification_uid: str = "purchase_order_update"

    action_text: str = _("Show Purchase Order")

    visibility: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    push: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    email: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    sms: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.DISABLED,
        NodeMemberType.ADMIN: NotificationCondition.DISABLED,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }

    email_template: str = "default.html"

    def get_title(self) -> str:
        return _("Purchase Order({po_num}) is updated").format(po_num=self.action_object.number)

    def get_body(self) -> str:
        return _("Purchase Order({po_num}) received from {name} under the {sc_name} supplychain is updated").format(
            po_num=self.action_object.number,
            name=self.action_object.sender.name,
            sc_name=self.action_object.product.supply_chain.name)

    def get_url_path(self):
        return f"purchase-order/order-details/receive/{self.action_object.idencode}/"
        
    def get_actor_node(self):
        return self.action_object.sender

    def get_target_node(self):
        return self.action_object.receiver

    def get_supply_chain(self):
        return self.action_object.product.supply_chain

    def get_redirect_id(self):
        return self.action_object.id

    def get_redirect_type(self):
        return 'receive'

    def get_tenant(self):
        return self.action_object.sender.tenant


class PurchaseOrderApprovalNotificationManager(BaseNotificationManager):
    """
    Notification manager for sending email notification and push notifications
    to reciever/sender node members that purchase order is approved, rejected or 
    cancelled.
    """

    notification_uid: str = "purchase_order_approval"

    action_text: str = _("Show Purchase Order")

    visibility: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    push: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    email: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    sms: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.DISABLED,
        NodeMemberType.ADMIN: NotificationCondition.DISABLED,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }

    email_template: str = "default.html"

    def get_title(self) -> str:
        status_text = {
            constants.PurchaseOrderStatus.PENDING: _('pending'),
            constants.PurchaseOrderStatus.APPROVED: _('approved'),
            constants.PurchaseOrderStatus.REJECTED: _('rejected'),
            constants.PurchaseOrderStatus.ON_HOLD: _('on hold'),
            constants.PurchaseOrderStatus.CANCELLED: _('cancelled'),
            constants.PurchaseOrderStatus.PARTIAL: _('partially fulfilled'),
        }[self.action_object.status]
        return _("Purchase Order({po_num}) is {status_text}").format(
            po_num=self.action_object.number,
            status_text=status_text)

    def get_body(self) -> str:
        status_text = {
            constants.PurchaseOrderStatus.PENDING: _('pending'),
            constants.PurchaseOrderStatus.APPROVED: _('approved'),
            constants.PurchaseOrderStatus.REJECTED: _('rejected'),
            constants.PurchaseOrderStatus.ON_HOLD: _('on hold'),
            constants.PurchaseOrderStatus.CANCELLED: _('cancelled'),
            constants.PurchaseOrderStatus.PARTIAL: _('partially fulfilled'),
        }[self.action_object.status]
        stock_desc = _("{kg_quantity}{unit} of {product}").format(
            kg_quantity=formats.localize(self.action_object.quantity, use_l10n=True),
            unit=self.action_object.unit.code,
            product=self.action_object.product.name)
        body = _("Purchase Order({po_num}) for {stock_desc} is {status_text}").format(
            po_num=self.action_object.number,
            stock_desc=stock_desc,
            status_text=status_text)
        if self.action_object.status in [
                constants.PurchaseOrderStatus.APPROVED,
                constants.PurchaseOrderStatus.REJECTED]:
            actor_text = _(" by {receiver}").format(receiver=self.action_object.receiver.name)
            body += actor_text
        return body

    def get_url_path(self):
        if self.action_object.status == constants.PurchaseOrderStatus.CANCELLED:
            return f"purchase-order/order-details/recieve/{self.action_object.idencode}/"
        else:
            return f"purchase-order/order-details/send/{self.action_object.idencode}/"

    def get_actor_node(self):
        actor = self.action_object.receiver
        if self.action_object.status == constants.PurchaseOrderStatus.CANCELLED:
            actor = self.action_object.sender
        return actor

    def get_target_node(self):
        target = self.action_object.sender
        if self.action_object.status == constants.PurchaseOrderStatus.CANCELLED:
            target = self.action_object.receiver
        return target

    def get_supply_chain(self):
        return self.action_object.product.supply_chain
    
    def get_redirect_id(self):
        return self.action_object.id

    def get_redirect_type(self):
        type = 'send'
        if self.action_object.status == constants.PurchaseOrderStatus.CANCELLED: 
            type = 'receive'
        return type

    def get_tenant(self):
        return self.action_object.sender.tenant


class TransactionCommentNotificationManager(BaseNotificationManager):
    """
    Notification manager for sending push notifications to node members 
    when a document is added under a transaction.
    """

    notification_uid: str = "transaction_comment"

    visibility: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    push: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    email: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.DISABLED,
        NodeMemberType.ADMIN: NotificationCondition.DISABLED,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    sms: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }

    def get_title(self) -> str:
        return _("New comment added under the transaction {trans_num}.").format(trans_num=self.action_object.transaction.number)

    def get_body(self) -> str:
        return _("New comment added under the transaction {trans_num} by {commenter}.").format(
            trans_num=self.action_object.transaction.number,
            commenter=self.action_object.updater.name)

    def get_actor_node(self):
        return self.action_object.member.node

    def get_target_node(self): # TODO : Temporary fix.
        # if self.action_object.transaction.source_node == self.action_object.member.node:
        #     return self.action_object.transaction.destination_node
        # return self.action_object.transaction.source_node
        member = NodeMember.objects.filter(
                user=self.user, node=self.action_object.transaction.source_node)
        if not member:
            member = NodeMember.objects.filter(
                user=self.user, node=self.action_object.transaction.destination_node)
        return member.first().node

    def get_supply_chain(self):
        return self.action_object.transaction.supply_chain

    def get_redirect_id(self):
        return self.action_object.transaction.id

    def get_redirect_type(self):
        type = 'external'
        if self.action_object.transaction.transaction_type == constants.TransactionType.INTERNAL:
            type = 'internal'
        return type

    def get_tenant(self):
        return self.action_object.transaction.tenant


class DeliveryNotificationManager(BaseNotificationManager):
    """
    Notification manager for sending push notifications to receiver that new 
    delivery notification send by the sender.
    """

    notification_uid: str = "delivery_notification"

    visibility: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    push: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    email: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }
    sms: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.ADMIN: NotificationCondition.IF_USER_ACTIVE,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }

    email_template: str = "default.html"

    def get_title(self) -> str:
        stock_desc = _("{kg_quantity}{unit} of {product}").format(
            kg_quantity=formats.localize(self.action_object.quantity, use_l10n=True),
            unit=self.action_object.purchase_order.unit.code,
            product=self.action_object.purchase_order.product.name)
        return _("{stock_desc} will be delivered on {date}.").format(
            stock_desc=stock_desc,
            date=change_date_format(self.action_object.expected_date))

    def get_body(self) -> str:
        stock_desc = _("{kg_quantity}{unit} of {product}").format(
            kg_quantity=formats.localize(self.action_object.quantity, use_l10n=True),
            unit=self.action_object.purchase_order.unit.code,
            product=self.action_object.purchase_order.product.name)
        return _("{stock_desc} will be delivered on {date} by {sender}.").format(
            stock_desc=stock_desc,
            date=change_date_format(self.action_object.expected_date),
            sender=self.action_object.purchase_order.receiver.name)

    def get_actor_node(self):
        return self.action_object.purchase_order.receiver

    def get_target_node(self):
        return self.action_object.purchase_order.sender

    def get_supply_chain(self):
        return self.action_object.purchase_order.product.supply_chain

    def get_redirect_id(self):
        return self.action_object.purchase_order.id

    def get_redirect_type(self):
        return "recieve"

    def get_tenant(self):
        return self.action_object.purchase_order.sender.tenant
