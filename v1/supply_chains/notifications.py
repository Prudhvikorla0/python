
from django.utils.translation import gettext_lazy as _

from base import session

from v1.notifications.manager import BaseNotificationManager
from v1.notifications.constants import NotificationCondition
from v1.nodes.constants import NodeMemberType


class NodeInviteNotificationManager(BaseNotificationManager):
    """
    Notification manager for sending email notification to node member when a
    connection is created or node is invited
    """
    notification_uid: str = "node_invite"

    action_text: str = _("Show Connection")
    url_path: str = "welcome"

    visibility: dict = {
        NodeMemberType.SUPER_ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.CONNECTION_MANAGER: NotificationCondition.ENABLED,
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
        NodeMemberType.SUPER_ADMIN: NotificationCondition.ENABLED,
        NodeMemberType.ADMIN: NotificationCondition.ENABLED,
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

    email_template: str = "add_connection.html"

    def get_title(self) -> str:
        return _("New connection from {source}").format(source=self.action_object.source.name)

    def get_body(self) -> str:
        return _(
            "{target_name} received a new connection from {source_name} in {sc_name} supply chain.").format(
                target_name=self.action_object.target.name,
                source_name=self.action_object.source.name,
                sc_name=self.action_object.supply_chain.name)

    def get_url_params(self) -> dict:
        return {
            'node_id': self.action_object.target.idencode,
            'connection_id': self.action_object.idencode,
        }

    def get_actor_node(self):
        return self.action_object.source

    def get_target_node(self):
        return self.action_object.target

    def get_supply_chain(self):
        return self.action_object.supply_chain

    def get_tenant(self):
        return self.action_object.tenant
