"""Filters used in the app product."""

from django_filters import filters
from django.forms import fields as form_fields

from utilities.functions import decode


class IdencodeFilter(filters.CharFilter):
    
    def filter(self, qs, value):
        if  value and ',' in value:
            value = [decode(id) for id in value.split(',') if id]
            self.lookup_expr = 'in'
            self.distinct = True
        elif value:
            value = decode(value)
        return super(IdencodeFilter, self).filter(qs, value)

class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass
