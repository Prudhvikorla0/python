"""Serializer used in accounts app not from accounts apps are stored here."""

from rest_framework import serializers

from common.drf_custom import fields as custom_fields

from v1.nodes import models as node_models


class UserNodeSerializer(serializers.ModelSerializer):
    """
    Serializer for node data in user details
    """
    id = custom_fields.IdencodeField(source='node.id')
    name = serializers.CharField(source='node.name')
    image = serializers.FileField(source='node.image')
    node_type = serializers.IntegerField(source='node.type')
    member_role = serializers.IntegerField(source='type')
    email = serializers.EmailField(source='node.email')

    class Meta:
        """Meta Info."""
        model = node_models.NodeMember
        fields = ('id', 'name', 'node_type', 'member_role', 'image', 'email')
