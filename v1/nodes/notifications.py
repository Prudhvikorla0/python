
from django.utils.translation import gettext_lazy as _

from base import session

from v1.notifications.manager import BaseNotificationManager
from v1.notifications.constants import NotificationCondition
from v1.nodes.constants import NodeMemberType


class MemberInviteNotificationManager(BaseNotificationManager):
    """
    Notification manager for sending email notification to node member when a
    connection is created or node is invited
    """
    notification_uid: str = "member_invite"

    action_text: str = _("Accept invitation")
    url_path: str = "welcome"

    visibility: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.ENABLED,
        NodeMemberType.REPORTER: NotificationCondition.ENABLED,
    }
    push: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.ENABLED,
        NodeMemberType.REPORTER: NotificationCondition.ENABLED,
    }
    email: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.ENABLED,
        NodeMemberType.REPORTER: NotificationCondition.ENABLED,
    }
    sms: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.DISABLED,
        NodeMemberType.ADMIN: NotificationCondition.DISABLED,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.TRANSACTION_MANAGER: NotificationCondition.DISABLED,
        NodeMemberType.REPORTER: NotificationCondition.DISABLED,
    }

    email_template: str = "member_invite.html"

    def get_title(self) -> str:
        return _("Team member invitation from {name}").format(name=self.action_object.node.name)

    def get_body(self) -> str:
        return _(
            "You have been invited to {ten_name}'s traceability portal to manage {node_name} by {inviter_name}.").format(
                ten_name=self.action_object.tenant.name,
                node_name=self.action_object.node.name,
                inviter_name=self.action_object.creator.name
        )

    def get_url_params(self) -> dict:
        return {
            'node_id': self.action_object.node.idencode,
        }

    def get_actor_node(self):
        return self.action_object.node

    def get_target_node(self):
        return self.action_object.node

    def get_supply_chain(self):
        return None

    def get_tenant(self):
        return self.action_object.tenant


class NodeDocumentNotificationManager(BaseNotificationManager):
    """
    Notification manager for notify node members that new documents added to the
    under the node.
    """

    notification_uid: str = "node_document_added"


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

    def get_title(self) -> str:
        return _("New company document added.")

    def get_body(self) -> str:
        if self.action_object.category:
            return _(
                "New company document added under the category {category}.").format(
                    category=self.action_object.category.name)
        return  _("New company document added.")

    def get_actor_node(self):
        return self.action_object.node

    def get_target_node(self):
        return self.action_object.node

    def get_supply_chain(self):
        return None

    def get_tenant(self):
        return self.action_object.node.tenant
