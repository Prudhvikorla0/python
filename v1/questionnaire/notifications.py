"""
Notifications in apiauth module
"""
from django.utils.translation import gettext_lazy as _

from v1.notifications.manager import BaseNotificationManager
from v1.notifications.constants import NotificationCondition
from v1.nodes.constants import NodeMemberType


class ShareQuestionnaireNotificationManager(BaseNotificationManager):
    """
    Notification for sending email notification for sharing questionnaire.
    """
    notification_uid: str = "share_questionnaire"
    action_text: str = _("Show Questionnaire")
    url_path: str = "public/questionnaire/"

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

    email_template: str = "public.html"

    def get_title(self) -> str:
        return _(
            "{node_name} shared a questionnaire named {questionnaire} to you. Shared link will be expired within 48 hours").format(questionnaire=self.action_object.name,node_name=self.action_object.owner.name)

    def get_body(self) -> str:
        return _(
            "{node_name} shared a questionnaire named {questionnaire} to you. Shared link will be expired within 48 hours").format(questionnaire=self.action_object.name,node_name=self.action_object.owner.name)


    def get_url_params(self) -> dict:
        return {
            'token': self.notification_object.validation_token.key,
            'salt': self.notification_object.validation_token.idencode,
            "questionnaire": self.action_object.idencode
        }

    def get_actor_node(self):
        return self.action_object.owner

    def get_target_node(self):
        return None

    def get_supply_chain(self):
        return None
    
    def get_send_to(self) -> str:
        return self.send_to
