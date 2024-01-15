"""Validators for Template fields"""
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email

from utilities.functions import validate_phone, decode, read_date


def check_empty(value, required):
    is_empty = False
    data = {
        "value": value,
        "message": "",
        "is_valid": True,
        "hidden": False
    }
    if not bool(value) and value not in [False, 0]:
        is_empty = True
        if required:
            data['message'] = _(f"Cannot be empty.")
            data['is_valid'] = False
    return data, is_empty


def pk_validator(value, required):
    """Validates a primary key"""
    data, is_empty = check_empty(value, required)
    data['hidden'] = True
    if is_empty:
        return data
    try:
        value = str(value)
        if value:
            decode(value)
        data['value'] = value
    except Exception as e:
        data['message'] += _(f"Invalid ID.")
        data['is_valid'] = False
    return data


def string_validator(value, required):
    """Validates a string"""
    data, is_empty = check_empty(value, required)
    if is_empty:
        return data
    try:
        value = str(value)
        data['value'] = value
    except Exception as e:
        data['message'] += _(f"Not a valid string of characters.")
        data['is_valid'] = False
    return data


def integer_validator(value, required):
    """Validates an integer value"""
    data, is_empty = check_empty(value, required)
    if is_empty:
        return data
    try:
        value = int(value)
        data['value'] = value
    except Exception as e:
        data['message'] += _(f"Not a valid Integer.")
        data['is_valid'] = False
    return data


def positive_integer_validator(value, required):
    """Validates an integer value"""
    data = integer_validator(value, required)
    if not data['is_valid']:
        return data
    try:
        if value <= 0:
            data['message'] += _(f"Should be a positve value.")
            data['is_valid'] = False
    except Exception as e:
        data['message'] += _(f"Not a valid Integer.")
        data['is_valid'] = False
    return data


def float_validator(value, required):
    """Validates a floating point number"""
    data, is_empty = check_empty(value, required)
    if is_empty:
        return data
    try:
        value = round(float(value), 3)
        data['value'] = value
    except Exception as e:
        data['message'] += _(f"Not a valid floating point number.")
        data['is_valid'] = False
    return data


def positive_float_validator(value, required):
    """Validates an integer value"""
    data = float_validator(value, required)
    if not data['is_valid']:
        return data
    try:
        if value <= 0:
            data['message'] += _(f"Should be a positve value.")
            data['is_valid'] = False
    except Exception as e:
        data['message'] += _(f"Not a valid floating point number.")
        data['is_valid'] = False
    return data


def date_validator(value, required):
    """Validates a date"""
    data, is_empty = check_empty(value, required)
    if is_empty:
        return data
    try:
        if type(value) is str:
            date = read_date(value)
        else:
            date = value
        value = date.strftime("%d-%m-%Y")
        data['value'] = value
    except Exception as e:
        data['message'] += _(f"Not a valid date string. Should DD-MM-YYYY'.")
        data['is_valid'] = False
    return data


def phone_validator(value, required):
    """Validates a phone number"""
    data, is_empty = check_empty(value, required)
    if is_empty:
        return data
    if value:
        validated_phone = validate_phone(value)
        if validated_phone:
            data['value'] = validated_phone
        else:
            data['message'] = _(f"Not a valid phone number.")
            data['is_valid'] = False
    return data


def email_validator(value, required):
    """Validates an email address"""
    data, is_empty = check_empty(value, required)
    if is_empty:
        return data
    if value:
        try:
            validate_email(value)
            data['value'] = value
        except Exception as e:
            data['message'] += _(f"Not a valid email address.")
            data['is_valid'] = False
    return data


def bool_validator(value, required):
    """Validates an email address"""
    true_values = ('y', 'yes', 'true', 't')
    false_values = ('n', 'no', 'false', 'f')
    data, is_empty = check_empty(value, required)
    if is_empty:
        return data
    if value:
        try:
            if type(value) is bool:
                data['value'] = value
            elif value.lower().strip() in true_values:
                data['value'] = True
            elif value.lower().strip() in false_values:
                data['value'] = False
            else:
                raise ValueError(_(f"Unrecognized Yes/No Value."))
        except Exception as e:
            data['message'] += _(f"Unrecognized Yes/No Value.")
            data['is_valid'] = False
    return data
