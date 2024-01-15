
import re
import pendulum
from django.utils.crypto import get_random_string


def formatter(fmt=""):
    """
    Function to generate random strings of a defined format.
    The while loop is used to generate different random strings for each
    occurrence of the placeholder.
    Available options are,

    d   : Current day in dd format
    m   : Current month in mm format
    y   : Current year in yy format
    Y   : Current year in yyyy format
    0r5  : 5 digit random alphanumeric string
    0r10 : 10 digit random alphanumeric string
    0R5  : 5 digit random capitalized alphanumeric string
    0R10 : 10 digit random capitalized alphanumeric string
    r5  : 5 digit random alphabet string
    r10 : 10 digit random alphabet string
    R5  : 5 digit random capitalized alphabet string
    R10 : 10 digit random capitalized alphabet string

    Example use as default for models

    from functools import partial
    ...
    code = models.CharField(
        max_length=500, null=True, blank=True,
        default=partial(formatter, "{Y}-{m}-{d}-{R10}"),
        verbose_name=_('Code'))
    """
    alphabets = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    today = pendulum.today()
    while re.findall(r'\{[^\}]*\}', fmt):
        sub_fmt = re.findall(r'\{[^\}]*\}', fmt)[0]
        variables = {
            'd': today.strftime('%d'),
            'm': today.strftime('%m'),
            'y': today.strftime('%y'),
            'Y': today.strftime('%Y'),
            'r5': get_random_string(5, allowed_chars=alphabets).lower(),
            'r10': get_random_string(10, allowed_chars=alphabets).lower(),
            'R5': get_random_string(5, allowed_chars=alphabets).upper(),
            'R10': get_random_string(10, allowed_chars=alphabets).upper(),
            '0r5': get_random_string(5).lower(),
            '0r10': get_random_string(10).lower(),
            '0R5': get_random_string(5).upper(),
            '0R10': get_random_string(10).upper(),
        }
        sub_str = sub_fmt.format(**variables)
        fmt = re.sub(sub_fmt, sub_str, fmt, 1)
    return fmt


