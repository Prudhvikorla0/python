"""Models of the app Accounts."""

import datetime

# from fcm_django.models import AbstractFCMDevice
import pendulum
from django.db import models
from django.contrib.auth.models import \
    AbstractUser as DjangoAbstractUser
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from common import library as common_lib
from base.models import AbstractBaseModel
from base.models import CustomUserManager
from base import session

from v1.accounts import constants as user_consts
from v1.apiauth import notifications
from v1.nodes import constants as node_constants


class CustomUser(DjangoAbstractUser, AbstractBaseModel):
    """
    Base User model.

    Attribs:
        dob(date): Date of birth of user.
        phone (str): phone number of the user.
        address(str): address of the user.
        language(int): Language preference.
        image (img): user image.
        type (int): Type of the user like
            admin ,node user or tenant user etc.
        status(int): Current status of the user like created or active.
        blocked(bool): field which shows the active status of user.
        updated_email(email): While updating email the new email is stored 
            here before email verification.

    Inherited Attribs:
        username(char): Username for the user for login.
        email(email): Email of the user.
        password(char): Password of the user.
        first_name(char): First name of the user.
        last_name(char): Last name of the user.
        date_joined(date): User added date.

    """
    dob = models.DateField(
        null=True, blank=True, verbose_name=_('Date Of Birth'))
    phone = models.CharField(
        default='', max_length=200, null=True, blank=True,
        verbose_name=_('Phone Number'))
    address = models.CharField(
        default='', max_length=2000, null=True, blank=True,
        verbose_name=_('Address'))
    language = models.CharField(
        max_length=10, verbose_name=_('Selected Language'),
        default=user_consts.Language.ENGLISH, 
        choices=user_consts.Language.choices)
    image = models.ImageField(
        upload_to=common_lib._get_file_path,
        null=True, default=None, blank=True, verbose_name=_('Photo'))
    type = models.IntegerField(
        default=user_consts.UserType.NODE_USER, 
        choices=user_consts.UserType.choices, verbose_name=_('User Type'))
    status = models.IntegerField(
        default=user_consts.UserStatus.CREATED, 
        choices=user_consts.UserStatus.choices, verbose_name=_('User Status'))
    is_blocked = models.BooleanField(
        default=False, verbose_name=_('Block User'))
    updated_email = models.EmailField(
        null=True, blank=True, default='', 
        verbose_name=_('Last Updated Email'))
    default_node = models.ForeignKey(
        'nodes.Node', null=True, on_delete=models.SET_NULL,
        blank=True, verbose_name=_("Default Node Of User"), 
        related_name='default_node_users')
    tenant = models.ForeignKey(
        'tenants.Tenant', null=True, on_delete=models.SET_NULL,
        blank=True, verbose_name=_("Tenant"), related_name='users')
    accepted_policy = models.ForeignKey(
        'accounts.PrivacyPolicy', null=True, on_delete=models.SET_NULL,
        blank=True, verbose_name=_("Latest Accepted Privacy Policy"), 
        related_name='accepted_users')
    force_logout = models.BooleanField(
        default=False, verbose_name=_("Force Logout User"))
    walkthrough_status = models.JSONField(
        default=dict, null=True, blank=True,
        verbose_name="WalkThrough Status")

    objects = CustomUserManager()

    class Meta:
        """Meta class for the above model."""

        verbose_name = ('Base User')

    def __str__(self):
        """Object name in django admin."""
        return f'{self.name} - {self.idencode}'

    def save(self, *args, **kwargs):
        if self.email:
            self.username = self.email
        else:
            self.username = get_random_string(32)
        return super(CustomUser, self).save(*args, **kwargs)

    @property
    def image_url(self):
        """Get file url ."""
        try:
            return self.image.url
        except:
            return None

    @property
    def name(self):
        """Get user full name."""
        return f'{self.get_full_name()}'

    def get_default_node(self):
        def_node = self.default_node
        if not def_node or def_node not in self.nodes.all():
            self.default_node = self.nodes.all().first()
            self.save()
        return self.default_node

    def set_default_node(self, node):
        if self.status == user_consts.UserStatus.ACTIVE:
            node.status = node_constants.NodeStatus.ACTIVE
            node.save()
        self.default_node = node
        self.save()
        return self.default_node

    def get_default_sc(self):
        """Method to return default supplychain"""
        try:
            def_sc = self.member_nodes.get(
                node=self.get_default_node()).get_default_sc()
            return def_sc
        except:
            return None

    def reset_password(self, ip="", location="", device=""):
        """Function to set password."""
        token = ValidationToken.initialize(
            self, user_consts.ValidationTokenType.RESET_PASS, ip, location, device)
        notification_manager = notifications.PasswordResetNotificationManager(
            user=self, action_object=token, token=token)
        notification_manager.send_notification()
        return True

    def set_active(self):
        self.status = user_consts.UserStatus.ACTIVE
        self.save()
        def_node = self.get_default_node()
        def_node.status = node_constants.NodeStatus.ACTIVE
        def_node.joined_on = pendulum.now()
        def_node.save()

    @property
    def policy_accepted(self):
        """
        Return privacy info related to the user.
        """
        if self.accepted_policy == PrivacyPolicy.current_privacy_policy():
           return True
        return False

    def user_config(self):
        """Return the permission to do activities in the system."""
        if self.type == user_consts.UserType.NODE_USER:
            member = self.member_nodes.get(
                node=session.get_current_node(), is_active=True)
            access_data = {
                    "can_edit_node_detail": False, 
                    "can_add_team_member": False, 
                    "can_create_connection": False, 
                    "can_create_transaction": False, 
                    "can_create_purchase_order": False
                }
            if member.type == node_constants.NodeMemberType.SUPER_ADMIN:
                access_data = {
                    "can_edit_node_detail": True, 
                    "can_add_team_member": True, 
                    "can_create_connection": True, 
                    "can_create_transaction": True, 
                    "can_create_purchase_order": True
                }
            elif member.type == node_constants.NodeMemberType.ADMIN:
                access_data = {
                    "can_edit_node_detail": True, 
                    "can_add_team_member": False, 
                    "can_create_connection": True, 
                    "can_create_transaction": True, 
                    "can_create_purchase_order": True
                }
            elif member.type == \
                node_constants.NodeMemberType.CONNECTION_MANAGER:
                access_data['can_create_connection'] = True
            elif member.type == \
                node_constants.NodeMemberType.TRANSACTION_MANAGER:
                access_data['can_create_transaction'] = True
            if (self.default_node.type == node_constants.NodeType.PRODUCER) or (
                self.tenant.non_producer_stock_creation == True):
                access_data.update({"can_create_stock": True})
            else:
                access_data.update({"can_create_stock": False})
        else:
            access_data = {}
        return access_data

    def make_force_logout(self):
        """Method makes force logout true"""
        self.force_logout = True
        self.save()
        return True

    def disable_force_logout(self):
        """Method to make force logout false."""
        self.force_logout = False
        self.save()
        return True

    def get_notification_pref(self, notif_manager):
        """
        Function to return notification preferences for a user.
        """
        from v1.notifications.constants import NotificationCondition
        def get_pref(config: dict) -> bool:
            if "__all__" not in config.keys():
                raise ValueError(_("Config not defined."))
            if config["__all__"] == NotificationCondition.ENABLED:
                return True
            elif config["__all__"] == NotificationCondition.DISABLED:
                return False
            elif config["__all__"] == NotificationCondition.IF_USER_ACTIVE:
                return self.status == user_consts.UserStatus.ACTIVE
            return False
        prefs = {
            "visibility": get_pref(notif_manager.visibility),
            "push": get_pref(notif_manager.push),
            "email": get_pref(notif_manager.email),
            "sms": get_pref(notif_manager.sms)
        }
        return prefs
    
    @property
    def node_members(self):
        """
        """
        managing_nodes = self.member_nodes.all()
        if session.get_current_tenant():
            managing_nodes = managing_nodes.filter(
                tenant=session.get_current_tenant())
        return managing_nodes


class ValidationToken(AbstractBaseModel):
    """
    Class to store the validation token data.

    This is a generic model to store and validate all
    sort of tokens including password setters, one time
    passwords and email validations..

    Attribs:
        user(obj): user object
        key (str): token.
        status(int): status of the validation token
        expiry(datetime): time up to which link is valid.
        type(int): type indicating the event associated.

    Inherited Attribs:
        creator(obj): Creator user of the object.
        updater(obj): Updater of the object.
        created_on(datetime): Added date of the object.
        updated_on(datetime): Last updated date of the object.
    """

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='validation_tokens', verbose_name=_('Token User'))

    ip = models.CharField(default='', max_length=500, blank=True)
    location = models.CharField(default='', max_length=500, blank=True)
    device = models.CharField(default='', max_length=500, blank=True)

    key = models.CharField(max_length=200, verbose_name=_('Token'))
    status = models.IntegerField(
        default=user_consts.ValidationTokenStatus.UNUSED, 
        choices=user_consts.ValidationTokenStatus.choices, 
        verbose_name=_('Token Status'))
    expiry = models.DateTimeField(
        default=timezone.now, verbose_name=_('Token Expiry Date'))
    type = models.IntegerField(
        default=user_consts.ValidationTokenType.VERIFY_EMAIL, 
        choices=user_consts.ValidationTokenType.choices, 
        verbose_name=_('Token Type'))

    def __str__(self):
        """Object name in django admin."""
        return f'{self.user.name} : {self.key} :  {self.id}'

    def save(self, *args, **kwargs):
        """
        Overriding the default save signal.

        This function will generate the token key based on the
        type of the token and save when the save() function
        is called if the key is empty. It. will. also set the
        expiry when the object is created for the first time.
        """
        if not self.key:
            self.key = self.generate_unique_key()
        if not self.id:
            self.expiry = self.get_expiry()
        return super(ValidationToken, self).save(*args, **kwargs)

    @property
    def creation_time_str(self):
        return pendulum.instance(self.created_on).format(
            "hh:mm A on dddd, DD-MM-YYYY")

    def get_validity_period(self):
        return user_consts.TOKEN_VALIDITY[self.type]

    def get_expiry(self):
        """Function to get the validity based on type."""
        validity = self.get_validity_period()
        return (timezone.now() + datetime.timedelta(
            minutes=validity))

    def generate_unique_key(self):
        """Function to generate unique key."""
        if self.type != user_consts.ValidationTokenType.OTP:
            key = get_random_string(settings.ACCESS_TOKEN_LENGTH)
        else:
            key = common_lib._generate_random_number(settings.OTP_LENGTH)

        if ValidationToken.objects.filter(
                key=key, type=self.type,
                status=user_consts.ValidationTokenStatus.UNUSED).exists():
            key = self.generate_unique_key()
        return key

    def validate(self):
        """Function to. validate the token."""
        status = True
        if not self.is_valid:
            status = False
        self.status = user_consts.ValidationTokenStatus.USED
        self.updater = self.user
        self.save()
        return status

    def refresh(self):
        """Function  to refresh the validation token."""
        if not self.is_valid:
            self.key = self.generate_unique_key()
            self.status = user_consts.ValidationTokenStatus.UNUSED
        self.expiry = self.get_expiry()
        self.updater = self.user
        self.save()
        return True

    def mark_as_used(self):
        """ Function to mark validation token as used """
        self.status = user_consts.ValidationTokenStatus.USED
        self.save()

    @staticmethod
    def initialize(user, type, ip="", location="", device=""):
        """Function to initialize verification."""
        if type in user_consts.REUSABLE_TOKENS:
            token = ValidationToken.objects.filter(
                type=type,user=user,notification=None
                ).order_by('-id').first()
            if token and token.is_reusable():
                return token
        token = ValidationToken.objects.create(
            user=user, status=user_consts.ValidationTokenStatus.UNUSED,
            type=type)
        token.ip = ip
        token.location = location
        token.device = device
        token.save()
        return token
    
    def expiry_remaining(self):
        """
        Return remaining hours for expiry.
        """
        remaining_hours = ((self.expiry - timezone.now()
                           ).total_seconds() / user_consts._1_HOUR_IN_SECONDS)
        return remaining_hours
    
    def is_reusable(self):
        """
        Check the token is reusable.
        """
        if self.is_valid() and (
            self.expiry_remaining() >= user_consts.REUSABLE_TOKEN_MINIMUM_HOURS):
            return True
        return False

    @property
    def validity(self):
        """Function to get the validity of token."""
        return common_lib._date_time_desc(self.expiry)

    @property
    def created_on_desc(self):
        """Function to get the validity of token."""
        return common_lib._date_time_desc(self.created_on)

    def is_valid(self):
        """Function  which check if Validator is valid."""
        if self.expiry > timezone.now() and (
                self.status == user_consts.ValidationTokenStatus.UNUSED):
            return True
        return False

    def invalidate(self):
        """
        Function chnage the status of the token into used and change the 
        expiry date of the token.
        """
        self.mark_as_used()
        self.expiry = timezone.now()
        self.save()
        return True
    
    def has_notification(self):
        """
        Returns true if the token linked with notification.
        """
        try:
            self.notification
            return True
        except:
            return False
        

class AccessToken(models.Model):
    """
    The default authorization token model.

    This model is overriding the DRF token
    Attribs:
        user(obj): user object
        Key(str): token
        created(datetime): created date and time.
        device(obj): device object
    """

    user = models.ForeignKey(
        CustomUser, related_name='authe_token',
        on_delete=models.CASCADE, verbose_name=_('Token User'))
    key = models.CharField(
        max_length=200, unique=True, verbose_name=_('Token'))
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Created Date'))
    device = models.ForeignKey(
        'accounts.UserDevice', on_delete=models.CASCADE,
        null=True, blank=True, verbose_name=_('Created Device'))

    def __str__(self):
        """Function to return value in django admin."""
        return self.key

    def save(self, *args, **kwargs):
        """Overriding the save method to generate key."""
        if not self.key:
            self.key = self.generate_unique_key()
        return super(AccessToken, self).save(*args, **kwargs)

    def generate_unique_key(self):
        """Function to generate unique key."""
        key = get_random_string(settings.ACCESS_TOKEN_LENGTH)
        if AccessToken.objects.filter(key=key).exists():
            self.generate_unique_key()
        return key

    def refresh(self):
        """Function  to change token."""
        self.key = self.generate_unique_key()
        self.save()
        return self.key


# class UserDevice(AbstractFCMDevice, AbstractBaseModel):
class UserDevice(AbstractBaseModel):
    """
    Class for user devices.

    This is inherited from the AbstractFCMDevice and
    AbstractBaseModel.

    Attribs:
        user(obj): user object.
        type(int): device types
    Attribs Inherited:
        name(str): name of the device
        active(bool): bool value.
        date_created(datetime): created time.
        device_id(str): Device id
        registration_id(str): Reg id
    """

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, 
        verbose_name=_('Device User'), related_name='devices')
    type = models.IntegerField(
        default=user_consts.DeviceType.ANDROID, 
        choices=user_consts.DeviceType.choices , 
        verbose_name=_('Device Type'))
    registration_id = models.TextField(
        verbose_name=_("Registration token"), blank=True, default='')

    class Meta:
        """Meta data."""

        verbose_name = _('User device')
        verbose_name_plural = _('User devices')

    def activate(self, types=user_consts.MOBILE_DEVICE_TYPES):
        """
        Function for set device as active and set other
        devices of same user as inactive.
        """
        for device in UserDevice.objects.filter(
                user=self.user, type__in=types):
            if device.active:
                device.active = False
                device.updater = self.user
                device.save()
        self.active = True
        self.save()
        return True

    def generate_token(self, force_create=False):
        """
        Function to create a unique token for a device.

        This function will create a token for the device if force create is
        true or retrieve the existing token and refresh it
        """
        response = {
            'is_granted': True,
            'token': ''
        }
        if not force_create:
            try:
                token = AccessToken.objects.get(
                    device=self, user=self.user, device__active=True)
                response['token'] = token.refresh()
            except:
                if not AccessToken.objects.filter(
                     user=self.user, device__active=True).exists():
                    response['token'] =\
                        self.user.issue_access_token(self)
                else:
                    response['is_granted'] = False
                    return response

            self.user.last_login = timezone.now()
            self.user.save()
            return response

        old_mobile_tokens = AccessToken.objects.filter(
            user=self.user, device__type__in=user_consts.MOBILE_DEVICE_TYPES)
        old_mobile_tokens.delete()
        response['token'] = self.user.issue_access_token(self)
        return response


class PrivacyPolicy(AbstractBaseModel):
    """
    Privacy Policy model.
    """
    content = models.TextField(
        default='', blank=True, null=True, 
        verbose_name=_('Policy Content'))
    version = models.PositiveIntegerField(
        default=0, verbose_name=_('Version'), unique=True)
    date = models.DateField(
        default=datetime.date.today, blank=True, null=True,
        verbose_name=_('Privacy Policy Date'))
    since = models.DateField(
        default=datetime.date.today, blank=True, null=True, 
        verbose_name=_('Start Date'))

    class Meta:
        """Meta data."""

        verbose_name_plural = _('Privacy Policies')
    
    def __str__(self):
        """
        Object value django admin.
        """
        return f'{self.version} : {self.since} - {self.idencode}'

    @staticmethod
    def latest_privacy_policy():
        """Return latest privacy policy"""
        return PrivacyPolicy.objects.latest('id')

    @staticmethod
    def current_privacy_policy():
        """Return current privacy policy"""
        return PrivacyPolicy.objects.exclude(
            since__gt=datetime.date.today()).latest('version')
