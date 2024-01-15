"""
Notifications in apiauth module
"""
from django.utils.translation import gettext_lazy as _

from v1.notifications.manager import BaseNotificationManager
from v1.notifications.constants import NotificationCondition
from v1.nodes.constants import NodeMemberType


class PasswordResetNotificationManager(BaseNotificationManager):
    """
    Notification for sending email notification for re-setting password
    """
    notification_uid: str = "password_reset"
    action_text: str = _("Change Password")
    url_path: str = "reset"

    visibility: dict = {
        "__all__": NotificationCondition.DISABLED
    }
    push: dict = {
        "__all__": NotificationCondition.DISABLED
    }
    email: dict = {
        "__all__": NotificationCondition.ENABLED
    }
    sms: dict = {
        "__all__": NotificationCondition.DISABLED
    }

    email_template: str = "reset_password.html"

    def get_title(self) -> str:
        return _("Received password reset request for your {tenant} Traceability Account").format(tenant=self.tenant.name)

    def get_body(self) -> str:
        return _("Received password reset request for your {tenant} Traceability Account").format(tenant=self.tenant.name)

    def get_url_params(self) -> dict:
        return {
            'token': self.action_object.key,
            'salt': self.action_object.idencode,
            'user_id': self.user.idencode,
        }

    def get_actor_node(self):
        return None

    def get_target_node(self):
        return None

    def get_supply_chain(self):
        return None
