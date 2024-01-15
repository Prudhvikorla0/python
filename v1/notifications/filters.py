"""Filters used in the app accounts."""

from django_filters import rest_framework as filters

from common.drf_custom import filters as custom_filters

from v1.notifications.models import Notification


class NotificationFilter(filters.FilterSet):
    """
    Filter for Notifications.
    """
    node = custom_filters.IdencodeFilter(field_name='target_node')
    is_read = filters.BooleanFilter()

    class Meta:
        model = Notification
        fields = ['node', 'is_read']
