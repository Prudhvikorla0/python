"""Commonly used helper function are defined here."""


from random import randint

from datetime import datetime
from time import mktime
from pytz import timezone

import phonenumbers

from rest_framework import status
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.utils.crypto import get_random_string
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation

from base.exceptions import BadRequest

from hashids import Hashids

from phonenumber_field.phonenumber import to_python


def _get_file_path(instance, filename):
    """
    Function to get filepath for a file to be uploaded
    Args:
        instance: instance of the file object
        filename: uploaded filename

    Returns:
        path: Path of file
    """
    type = instance.__class__.__name__.lower()
    path = '%s/%s/%s:%s' % (
        type, instance.id,
        get_random_string(10), filename)
    return path


def _validate_phone(number):
    """
    Function to validate phone number.

    Input Params:
        number(str): international phone number
    Returns:
        dictionary with
        phone(str): phone number
        code(str): country code
    """
    try:
        number = number.replace(' ', '')
        number = number.replace('-', '')
        number = phonenumbers.parse(number)
        phone = str(number.national_number)
        code = '+' + str(number.country_code)
        return code + phone
    except:
        return None


def _split_phone(number):
    """
    Function to split phone number into dial code and phone number.

    Args:
        number: concatenated phone number
    Returns:
        dial_code: International dialing code
        phone: National phone number.
    """
    number = number.replace(' ', '')
    number = number.replace('-', '')
    try:
        number = phonenumbers.parse(number)
        phone = str(number.national_number)
        code = '+' + str(number.country_code)
        return code, phone
    except:
        return '', number


def _validate_password(password):
    """
    Function to validate password.

    Input Params:
        password(str): password.
    Returns:
        valid(bool): valid status.
        message(str): validity message.
    """
    try:
        password_validation.validate_password(password)
        valid = True
        message = 'Valid Password.'
    except ValidationError as e:
        valid = False
        message = '; '.join(e.messages)
    return (valid, message)


def _generate_random_number(digits):
    """
    Function to generate n dig random number.

    Input Params:
        digits(int): number of digits
    Returns:
        (int): number
    """
    range_start = 10**(digits - 1)
    range_end = (10**digits) - 1
    return randint(range_start, range_end)


def _date_time_desc(date):
    """Function to format date time."""
    try:
        date = localtime(date)
    except:
        pass
    date = date.strftime('%d %B %Y, %H:%M %p')
    date += ', Timezone: %s' % settings.TIME_ZONE
    return date


def _unix_to_datetime(unix_time):
    """Function to convert Unix timestamps to date time."""
    try:
        unix_time = float(unix_time)
        localtz = timezone(settings.TIME_ZONE)
        date = localtz.localize(datetime.fromtimestamp(unix_time))
        return date
    except:
        raise BadRequest('Unix timestamps must be float or int')



def _datetime_to_unix(date):
    """Function to convert Unix timestamps to date time."""
    try:
        unix = mktime(date.timetuple())
    except:
        unix = 0.0

    return unix


def _string_date_to_unix(date):
    """Function to convert strng date to unix."""
    date = datetime.strptime(date, '%d-%m-%Y')
    return _datetime_to_unix(date)


def _pop_out_from_dictionary(dictionary, keys):
    """
    Function to remove keys from dictionary.

    Input Params:
        dictionary(dict): dictionary
        keys(list)
    Returns:
        dictionary(dictionary): updated dictionary.
    """
    for key in keys:
        dictionary.pop(key, None)
    return dictionary


def change_date_format(date=None):
    """Function changes date format to dd-mm-YYYY"""
    if date:
        try:
            str_date = str(date.date())
        except:
            str_date = str(date)
        return datetime.strptime(str_date, '%Y-%m-%d').strftime('%d-%m-%Y')


class PhoneNumberField(serializers.CharField):
    default_error_messages = {"invalid": _("Enter a valid phone number.")}

    def to_internal_value(self, data):
        phone_number = to_python(data)
        if phone_number and not phone_number.is_valid():
            raise ValidationError(self.error_messages["invalid"])
        return phone_number
    
def string_date_to_date(str_date, format='%Y-%m-%d'):
    """Function changes string date to date object."""
    date = datetime.strptime(str_date, format)
    return date
