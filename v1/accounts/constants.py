"""Constants under the user accounts section are stored here."""

from django.db import models
from django.utils.translation import gettext_lazy as _


# Validity in Minutes
_30_MINUTES = 30  # 30 Minutes
_1_DAY = 1440  # 24 hours
_2_DAY = 2880  # 48 hours
_365_DAYS = 525600  # 365 days

# Validity in seconds

_1_HOUR_IN_SECONDS = 3600 # seconds


class Language(models.TextChoices):
    ENGLISH = "en", _('English')
    DUTCH = "nl", _('Dutch')
    GERMAN = "de", _('German')
    FRENCH = "fr", _('French')


class UserType(models.IntegerChoices):
    TENANT_USER = 101, _('Tenant User')
    NODE_USER = 111, _('Node User')
    ADMIN = 121, _('ADMIN')


class UserStatus(models.IntegerChoices):
    CREATED = 101, _('User Created')
    ACTIVE = 111, _('User Active')


class ValidationTokenStatus(models.IntegerChoices):
    USED = 101, _('Used')
    UNUSED = 111, _('Unused')


class ValidationTokenType(models.IntegerChoices):
    VERIFY_EMAIL = 101, _('Verify Email')
    CHANGE_EMAIL = 102,  _('Change Email')
    RESET_PASS = 103,  _('Reset Password')
    OTP = 104,  _('OTP')
    MAGIC_LOGIN = 105,  _('Magic Login')
    INVITE = 106,  _('Invite')
    NOTIFICATION = 107,  _('Notification')
    QUESTIONNAIRE_SHARE = 108, _('Questionnaire Share')
    QUESTIONNAIRE_LINK = 109, _('Questionnaire Link')


class DeviceType(models.IntegerChoices):
    ANDROID = 101, _('Android')
    IOS = 102, _('Ios')
    WEB = 103, _('Web')

MOBILE_DEVICE_TYPES = [DeviceType.ANDROID, DeviceType.IOS]


# Validity
TOKEN_VALIDITY = {
    ValidationTokenType.VERIFY_EMAIL: _365_DAYS,
    ValidationTokenType.CHANGE_EMAIL: _365_DAYS,
    ValidationTokenType.RESET_PASS: _2_DAY,
    ValidationTokenType.OTP: _30_MINUTES,
    ValidationTokenType.MAGIC_LOGIN: _2_DAY,
    ValidationTokenType.INVITE: _365_DAYS,
    ValidationTokenType.NOTIFICATION: _365_DAYS,
    ValidationTokenType.QUESTIONNAIRE_SHARE: _2_DAY,
    ValidationTokenType.QUESTIONNAIRE_LINK: _2_DAY
}

# Reusable token

REUSABLE_TOKENS = [
    ValidationTokenType.QUESTIONNAIRE_LINK,
]
REUSABLE_TOKEN_MINIMUM_HOURS = 2 # HOURS
