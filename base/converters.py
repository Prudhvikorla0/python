"""
This file is to convert id
"""
from django.conf import settings
from utilities.functions import decode, encode


class IDConverter:
    """
    Converter to convert encoded id in url to integer id
    """
    regex = f"[{settings.HASHID_ALPHABETS}]{{{settings.HASHID_MIN_LENGTH},}}"

    def to_python(self, value):
        return decode(value)

    def to_url(self, value):
        return encode(value)
