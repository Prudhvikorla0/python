
from urllib.parse import urlencode
from django.utils.translation import gettext_lazy as _
from django.utils import translation

from base import session
from utilities.translations import internationalize_attribute

from v1.notifications.models import Notification
from v1.notifications.constants import NotificationCondition

NOTIFICATION_TYPES = {}


class BaseNotificationManager:
    """
    Base class to use for notifications.
    Notifications should be defined in the corresponding apps
    after inheriting from this base class.
    """
    notification_uid: str = ""

    action_text: str = _("Dashboard")
    url_path: str = "/notifications/"

    visibility: dict = {
        "__all__": NotificationCondition.ENABLED
    }
    push: dict = {
        "__all__": NotificationCondition.IF_USER_ACTIVE
    }
    email: dict = {
        "__all__": NotificationCondition.IF_USER_ACTIVE
    }
    sms: dict = {
        "__all__": NotificationCondition.DISABLED
    }

    email_template: str = "default.html"

    def __init__(
            self, user, action_object, token=None, context=None,send_to=None):
        """
        Initialize notification
        """
        from v1.nodes.models import NodeMember
        curr_language = translation.get_language()
        context = context or {}
        self.user = user
        self.action_object = action_object
        self.send_to = send_to
        self.tenant = self.get_tenant()
        target_node = self.get_target_node()
        member = NodeMember.objects.filter(node=target_node, user=user).first()
        self.notification_object = None
        if not member:
            self.visibility = {
                    "__all__": NotificationCondition.ENABLED
                    }
            self.push = {
                    "__all__": NotificationCondition.IF_USER_ACTIVE
                    }
            self.email = {
                    "__all__": NotificationCondition.IF_USER_ACTIVE
                    }
            self.sms= {
                    "__all__": NotificationCondition.DISABLED
                    }
        notif_prefs = member.get_notification_pref(self) if member \
            else user.get_notification_pref(self)
        if any(notif_prefs.values()):

            # action_object_class = action_object.__class__
            notification, created = Notification.objects.get_or_create(
                user=user,
                tenant=self.tenant,
                type=self.notification_uid,
                visibility=notif_prefs["visibility"],
                action_push=notif_prefs["push"],
                action_email=notif_prefs["email"],
                action_sms=notif_prefs["sms"],
                event_id= action_object.id,
                validation_token=token,
            )
            self.notification_object = notification

            internationalize_attribute(notification, 'title', self.get_title)
            internationalize_attribute(notification, 'body', self.get_body)

            notification.action_url = self.get_action_url()
            notification.actor_node = self.get_actor_node()
            notification.target_node = self.get_target_node()
            notification.supply_chain = self.get_supply_chain()
            notification.send_to = self.get_send_to()
            notification.context = context
            notification.event = action_object
            notification.redirect_id = self.get_redirect_id()
            notification.redirect_type = self.get_redirect_type()
            notification.save()
            self.notification_object = notification

    def send_notification(self):
        if not self.notification_object:
            return False
        return self.notification_object.send()

    def get_tenant(self):
        return session.get_current_tenant()

    def get_action_url(self) -> str:
        url = self.tenant.get_base_url()
        url = url / self.get_url_path()
        params = self.get_url_params()
        params['notification_id'] = self.notification_object.idencode
        params['user'] = self.user.idencode
        params['language'] = self.user.language
        if self.notification_object.validation_token:
            params['token'] = self.notification_object.validation_token.key
            params['salt'] = self.notification_object.validation_token.idencode
        url.add_params(**params)
        return url

    def get_title(self) -> str:
        return f"Notification for {self.user.username} for {self.action_object}."

    def get_body(self) -> str:
        return f"Notification for {self.user.username} for {self.action_object}."

    def get_url_path(self):
        return self.url_path

    def get_url_params(self) -> dict:
        return {}

    def get_send_to(self) -> str:
        return self.user.email

    def get_actor_node(self):
        raise NotImplementedError()

    def get_target_node(self):
        raise NotImplementedError()

    def get_supply_chain(self):
        raise NotImplementedError()

    def get_redirect_id(self):
        return None

    def get_redirect_type(self):
        return ''


def validate_notifications():
    from v1.nodes.constants import NodeMemberType
    def check_pref(pref: dict) -> bool:
        pref_keys = pref.keys()
        if "__all__" in pref_keys:
            if len(pref_keys) == 1:
                return True
            raise AssertionError(_("Cannot specify '__all__' and Member Types together"))
        for member_type in NodeMemberType:
            if member_type not in pref_keys:
                raise AssertionError(
                    _("Notification preference not defined for {member_type}").format(
                        member_type=NodeMemberType(member_type).label))
        return True

    for notification_type in BaseNotificationManager.__subclasses__():
        check_pref(notification_type.visibility)
        check_pref(notification_type.push)
        check_pref(notification_type.email)
        check_pref(notification_type.sms)
        uid = notification_type.notification_uid
        if not uid:
            raise AssertionError(
                _("Blank 'notification_uid' for {notif_name}. notification_uid cannot be blank"
                  ).format(notif_name=notification_type.__name__))
        elif uid in NOTIFICATION_TYPES.keys():
            raise AssertionError(
                _(f"notification_uid should be Unique. "
                  f"The value '{uid}' is already in use."))
        NOTIFICATION_TYPES[uid] = notification_type
