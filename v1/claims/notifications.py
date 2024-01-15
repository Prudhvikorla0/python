
from django.utils.translation import gettext_lazy as _

from base import session

from v1.notifications.manager import BaseNotificationManager
from v1.notifications.constants import NotificationCondition
from v1.nodes.constants import NodeMemberType

from v1.claims import constants as claim_consts


class ClaimAddedNotificationManager(BaseNotificationManager):
    """
    Notification manager for sending email notification and push notification to
    claim verifiers.
    """

    notification_uid: str = "claim_attachment"

    action_text: str = _("Show Batch")

    visibility: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.ADMIN: NotificationCondition.ENABLED,
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
        if self.action_object.attached_to == claim_consts.ClaimAttachedTo.NODE:
            return _("{claim_name} claim added to the company {node_name}.").format(
                claim_name=self.action_object.claim.name,
                node_name=self.action_object.get_node().name)
        elif self.action_object.attached_to == claim_consts.ClaimAttachedTo.BATCH:
            return _("{claim_name} claim added to the batch {batch_name} of {node_name}.").format(
                claim_name=self.action_object.claim.name,
                batch_name=self.action_object.get_batch().name,
                node_name=self.action_object.get_node().name)
        else:
            return _("{claim_name} claim added.").format(claim_name=self.action_object.claim.name)

    def get_body(self) -> str:
        if self.action_object.attached_to == claim_consts.ClaimAttachedTo.BATCH:
            return _(
                "{attached_by} attached claim named {claim_name} to the batch {batch_name} of {node_name} under {sc_name} supply chain.").format(
                    attached_by=self.action_object.attached_by.name,
                    claim_name=self.action_object.claim.name,
                    batch_name=self.action_object.get_batch().name,
                    node_name=self.action_object.get_node().name,
                    sc_name=self.action_object.supply_chain
                )
        if self.action_object.attached_to == claim_consts.ClaimAttachedTo.NODE:
            self.action_text = _("Show Company")
            return _(
                "{attached_by} attached claim named {claim_name} to the company {node_name}").format(
                    attached_by=self.action_object.attached_by.name,
                    claim_name=self.action_object.claim.name,
                    node_name=self.action_object.get_node().name,
                )
        else:
            return _(
                "{attached_by} attached claim named {claim_name} to the connection {connection}").format(
                    attached_by=self.action_object.attached_by.name,
                    claim_name=self.action_object.claim.name,
                    connection=self.action_object.connection.name,
                )

    def get_actor_node(self):
        return self.action_object.get_node()

    def get_target_node(self):
        return self.action_object.verifier

    def get_supply_chain(self):
        return self.action_object.supply_chain_object()

    def get_tenant(self):
        return self.action_object.claim.tenant

    # claim redirecting url is not added.


class ClaimVerifiedNotificationManager(BaseNotificationManager):
    """
    Notification manager for sending email notification and push notifications to
    claim attached node members.
    """

    notification_uid: str = "claim_verification"

    action_text: str = _("View Batch")

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
        if self.action_object.attached_to == claim_consts.ClaimAttachedTo.BATCH:
            if self.action_object.status == claim_consts.ClaimStatus.APPROVED:
                return _("{claim_name} of the {batch_name} is approved").format(
                    claim_name=self.action_object.claim.name,
                    batch_name=self.action_object.get_batch().name)
            elif self.action_object.status == claim_consts.ClaimStatus.REJECTED:
                return _("{claim_name} of the {batch_name} is rejected").format(
                    claim_name=self.action_object.claim.name,
                    batch_name=self.action_object.get_batch().name)
        else:
            self.action_text = _("Show Company")
            if self.action_object.status == claim_consts.ClaimStatus.APPROVED:
                return _("{claim_name} is approved").format(claim_name=self.action_object.claim.name)
            elif self.action_object.status == claim_consts.ClaimStatus.REJECTED:
                return _("{claim_name} is rejected").format(claim_name=self.action_object.claim.name)

    def get_body(self) -> str:
        if self.action_object.attached_to == claim_consts.ClaimAttachedTo.BATCH:
            if self.action_object.status == claim_consts.ClaimStatus.APPROVED:
                return _("{claim_name} Claim of the batch {batch_name} is approved by {name}").format(
                    claim_name=self.action_object.claim.name,
                    batch_name=self.action_object.get_batch().name,
                    name=self.action_object.verifier.name)
            elif self.action_object.status == claim_consts.ClaimStatus.REJECTED:
                return _("{claim_name} Claim of the batch {batch_name} is rejected by {name}").format(
                    claim_name=self.action_object.claim.name,
                    batch_name=self.action_object.get_batch().name,
                    name=self.action_object.verifier.name)
        else:
            if self.action_object.status == claim_consts.ClaimStatus.APPROVED:
                return _("{claim_name} Claim of the company {node_name} is approved by {name}").format(
                    claim_name=self.action_object.claim.name,
                    node_name=self.action_object.get_node().name,
                    name=self.action_object.verifier.name)
            elif self.action_object.status == claim_consts.ClaimStatus.REJECTED:
                return _("{claim_name} Claim of the company {node_name} is rejected by {name}").format(
                    claim_name=self.action_object.claim.name,
                    node_name=self.action_object.get_node().name,
                    name=self.action_object.verifier.name)
    
    def get_url_path(self):
        if self.action_object.attached_to == claim_consts.ClaimAttachedTo.BATCH:
            return f"stock/stock-details/{self.action_object.batch.idencode}/"
        else:
            return f"/company-profile/"

    def get_actor_node(self):
        return self.action_object.verifier

    def get_target_node(self):
        return self.action_object.get_node()

    def get_supply_chain(self):
        return self.action_object.supply_chain_object()

    def get_redirect_id(self):
        if self.action_object.attached_to == claim_consts.ClaimAttachedTo.BATCH:
            return self.action_object.batch.id
        return None

    def get_tenant(self):
        return self.action_object.claim.tenant


class ClaimCommentNotificationManager(BaseNotificationManager):
    """
    Notification manager for sending push notifications to node members 
    when a document/comment is added under a attached claim.
    """

    notification_uid: str = "added_claim_comment"

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
        NodeMemberType.SUPER_ADMIN: NotificationCondition.DISABLED,
        NodeMemberType.ADMIN: NotificationCondition.DISABLED,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }

    def get_title(self) -> str:
        return _("New comment added under the attached claim {claim_name}").format(claim_name=self.action_object.attached_claim.claim.name)

    def get_body(self) -> str:
        return _("New comment added under the attached claim {claim_name} by {name}").format(
            claim_name=self.action_object.attached_claim.claim.name,
            name=self.action_object.updater.name)

    def get_actor_node(self):
        return self.action_object.member.node

    def get_target_node(self):
        target = self.action_object.attached_claim.verifier
        if self.action_object.member.node == \
            self.action_object.attached_claim.verifier:
            target = self.action_object.attached_claim.attached_by
        return target

    def get_supply_chain(self):
        return self.action_object.attached_claim.supply_chain_object()

    def get_redirect_id(self):
        return self.action_object.attached_claim.id

    def get_tenant(self):
        return self.action_object.member.tenant
