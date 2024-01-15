"""
Serializers for notifications.
"""

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from common.drf_custom import fields

from v1.notifications.models import Notification

from v1.accounts.serializers import user as user_serializers


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer to get summary of count of notifications per node per user
    """
    id = fields.IdencodeField()
    actor_node = fields.IdencodeField()
    target_node = fields.IdencodeField()
    supply_chain = fields.IdencodeField()
    event_id = fields.IdencodeField()
    created_on = fields.UnixDateField()
    event_type = serializers.CharField(source='event_type.name', default=None)
    redirect_id = fields.IdencodeField()
    creator = fields.IdencodeField(
        serializer=user_serializers.BasicUserSerializer, read_only=True)

    class Meta:
        model = Notification
        fields = (
            'id', 'is_read', 'title', 'body', 'actor_node',
            'target_node', 'supply_chain', 'event_id', 'event_type', 
            'created_on', 'redirect_id', 'redirect_type', 'creator'
        )


class ReadNotificationSerializer(serializers.Serializer):
    """
    Serializer to read notifications
    """

    ids = fields.ManyToManyIdencodeField(
        required=False, related_model=Notification)
    all = serializers.BooleanField(required=False, default=False)

    class Meta:
        fields = ('ids', 'all')

    def validate(self, attrs):
        if 'ids' in attrs and attrs['ids']:
            return attrs
        if 'all' in attrs and attrs['all']:
            return attrs
        raise serializers.ValidationError(
            _("Either 'ids' should be mentioned or 'all' should be True"))

    def create(self, validated_data):
        notifications = Notification.objects.all()
        if 'ids' in validated_data and validated_data['ids']:
            notifications = notifications.filter(id__in=validated_data['ids'])
        notifications.update(is_read=True)
        return {}

    def to_representation(self, instance):
        return instance

