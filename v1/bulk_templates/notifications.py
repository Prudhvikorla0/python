
from django.utils.translation import gettext_lazy as _

from base import session

from v1.notifications.manager import BaseNotificationManager
from v1.notifications.constants import NotificationCondition
from v1.nodes.constants import NodeMemberType

from v1.bulk_templates import constants


class BulkUploadNotificationManager(BaseNotificationManager):
    """
    Notification manager for sending email notification and push notifications
    to the initiator of the bulk upload.
    """

    notification_uid: str = "bulk_upload_completed"

    action_text: str = _("Show BulkUpload")

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
        if self.action_object.status == constants.BulkUploadStatuses.COMPLETED:
            return _("Bulk upload of {bu_name}s from file {file_name} is completed.").format(
                bu_name=self.action_object.template.get_type_display(),
                file_name=self.action_object.file_name
            )
        else:
            return _("Bulk upload of {bu_name}s from file {file_name} is failed.").format(
                bu_name=self.action_object.template.get_type_display(),
                file_name=self.action_object.file_name
            )

    def get_body(self) -> str:
        if self.action_object.status == constants.BulkUploadStatuses.COMPLETED:
            return _("Bulk upload of {bu_name}s from file {file_name} is completed.").format(
                bu_name=self.action_object.template.get_type_display(),
                file_name=self.action_object.file_name
            )
        else:
            return _("Bulk upload of {bu_name}s from file {file_name} is failed.").format(
                bu_name=self.action_object.template.get_type_display(),
                file_name=self.action_object.file_name
            )

    def get_url_path(self):
        return f"bulk-upload/details?type={self.action_object.template.type}&id={self.action_object.idencode}"

    def get_actor_node(self):
        return self.action_object.node

    def get_target_node(self):
        return self.action_object.node

    def get_supply_chain(self):
        return self.action_object.supply_chain

    def get_redirect_id(self):
        return self.action_object.id

    def get_tenant(self):
        return self.action_object.tenant
