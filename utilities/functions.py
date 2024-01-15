"""
Utility functions used across apps
"""

import pytz
import hashlib
import requests
import calendar
import phonenumbers
from hashids import Hashids
from datetime import datetime
from datetime import date
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from ua_parser import user_agent_parser

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.functional import Promise


def encode(value):
    """
    Function to hash encode an integer value.

    Input Params:
        value(int): int value
    Returns:
        hashed string.
    """
    hasher = Hashids(
        min_length=settings.HASHID_MIN_LENGTH,
        salt=settings.HASHID_SALT,
        alphabet=settings.HASHID_ALPHABETS,
    )
    try:
        value = int(value)
        return hasher.encode(value)
    except Exception as e:
        raise ValueError(_("Invalid input {value} for Encoder. Should be of type int").format(value=value))


def is_decodable(value):
    """
    Function to hash decode an encoded value to int.

    Input Params:
        value(str): str value
    Returns:
        int value.
    """
    hasher = Hashids(
        min_length=settings.HASHID_MIN_LENGTH,
        salt=settings.HASHID_SALT,
        alphabet=settings.HASHID_ALPHABETS,
    )
    return bool(hasher.decode(value))


def decode(value):
    """
    Function to hash decode an encoded value to int.

    Input Params:
        value(str): str value
    Returns:
        int value.
    """
    hasher = Hashids(
        min_length=settings.HASHID_MIN_LENGTH,
        salt=settings.HASHID_SALT,
        alphabet=settings.HASHID_ALPHABETS,
    )
    try:
        return hasher.decode(value)[0]
    except Exception as e:
        raise ValueError(_("Invalid input({value}) for Decoder.").format(value=value))


def validate_phone(number):
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
        if not number.startswith('+'):
            number = '+' + number
        number = phonenumbers.parse(number)
        phone = str(number.national_number)
        code = '+' + str(number.country_code)
        return code + phone
    except Exception as e:
        print(e)
        return None


def list_to_sentence(word_list):
    """Function to convert list to sentence."""
    word_list = list(map(str, word_list))
    if not word_list[:-1]:
        return ' '.join(word_list)
    return "%s %s %s" % (', '.join(word_list[:-1]), _('and'), word_list[-1])


def hash_file(file):
    """
    Function to compute the hash of a file

    Args:
        file: file to be hashed.

    Returns:

    """
    if not file:
        return ''
    md5 = hashlib.md5()
    for chunk in file.chunks():
        md5.update(chunk)
    return md5.hexdigest()


def serialize_promises(data):
    """
    Function to serialize complex data structures with promises.
    """
    if isinstance(data, list):
        return [serialize_promises(i) for i in data]
    if isinstance(data, tuple):
        return (serialize_promises(i) for i in data)
    if isinstance(data, dict):
        return {serialize_promises(k): serialize_promises(v) for k, v in data.items()}
    if isinstance(data, Promise):
        return str(data)
    return data


def read_date(time_string: str) -> datetime.date:
    """
    Reads date from most common date string formats.
    Note :  It does not support the middle-endian format of USA
    """
    time_string = " ".join(time_string.replace(',', ' ').split()).title()
    formats = [
        '%d-%m-%Y', '%d/%m/%Y', '%d %m %Y', '%d.%m.%Y',  # 18-12-2020
        '%Y-%m-%d', '%Y/%m/%d', '%Y %m %d', '%Y.%m.%d',  # 2020-12-18
        '%b %d %Y', '%B %d %Y',  # Dec 18 2022 or December 18 2020
        '%d %b %Y', '%d %B %Y',  # 18 Dec 2022 or 18 December 2020
        '%d-%m-%y', '%d/%m/%y', '%d %m %y', '%d.%m.%y'  # 18-12-20
        '%y/%m/%d', '%y-%m-%d', '%y %m %d', '%y.%m.%d',  # 20-12-18
    ]
    for fmt in formats:
        try:
            date = datetime.strptime(time_string, fmt).date()
            return date
        except ValueError:
            continue
    else:
        raise ValueError('Not a valid date.')


def percentage(value, total):
    """
    Calculates the percentage without zerodivision error.
    If total is 0. returns 0 without raising error.
    Args:
        value: Value to convert to percentage
        total: Total value

    Returns:
        percentage: Percentage
    """
    try:
        if not value or not total:
            return 0.0
        return round((float(value) / float(total)) * 100, 2)
    except ZeroDivisionError:
        return 0.0


def get_ip_from_request(request):
    """
    Function to get the IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def get_location_from_ip(ip):
    """
    Function to get the location data from the IP address.
    """
    location_data = requests.get(settings.IP_API_URL.format(ip=ip)).json()
    location_info = [location_data.get(i) for i in ['city', 'region', 'country_name'] if location_data.get(i, None)]
    return ', '.join(location_info)


def device_name_from_request(request):
    """
    Function to get the device details from the request
    """
    user_agent_string = request.headers['User-Agent']
    user_agent = user_agent_parser.Parse(user_agent_string)
    brand = user_agent['device'].get('brand', 'Unknown')
    model = user_agent['device'].get('model', 'Device')
    device = ' '.join(i for i in [brand, model] if i)
    family = user_agent['user_agent']['family']
    os = user_agent['os']['family']
    browser_device = ' on '.join(i for i in [family, device] if i)
    device_string = ' running '.join(i for i in [browser_device, os] if i)
    return device_string


def client_details(request):
    """
    Get IP, Location and device of requester
    """
    ip = get_ip_from_request(request)
    location = get_location_from_ip(ip)
    device = device_name_from_request(request)
    return ip, location, device


def encode_list(id_list):
    """
    Function encodes list of ids.
    """
    return [encode(id) for id in id_list]


def decode_list(id_list):
    """
    Function decodes list of encoded ids.
    """
    return [decode(id) for id in id_list]


def week_start_end():
    today = date.today()
    start_date = today - timedelta(today.weekday())
    end_date = start_date + timedelta(6)
    return start_date, end_date


def month_start_end():
    today = date.today()
    start_date = date(today.year, today.month, 1)
    _, num_days = calendar.monthrange(today.year, today.month)
    end_date = date(today.year, today.month, num_days)
    return start_date, end_date


def start_of_day(day):
    return datetime(
        day.year, day.month, day.day, hour=00, minute=00, second=00,
        tzinfo=pytz.timezone(settings.TIME_ZONE))


def end_of_day(day):
    return datetime(
        day.year, day.month, day.day, hour=23, minute=59, second=59,
        tzinfo=pytz.timezone(settings.TIME_ZONE))


def get_start_end_time(day):
    start_time = start_of_day(day)
    end_time = end_of_day(day)
    return start_time, end_time


def get_past_months(date,range_value=12):
    """
    Return past months of a date.
    """
    date = date.replace(day=1)
    past_dates = [date,]
    for i in range(range_value-1):
        past_date = date - relativedelta(months=i+1)
        past_dates.append(past_date)
    return past_dates


def split_list(values,splitter,part1=False,part2=False):
    """
    Function to split list into two.
    """
    index = values.index(splitter)
    if part1:
        return values[:index]
    return values[index:] 
