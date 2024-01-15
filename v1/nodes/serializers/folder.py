"""Serializer related to folder."""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from common.drf_custom import fields as custom_fields
from base import session
from base import exceptions

from v1.nodes import models as node_models


class FolderSerializer(serializers.ModelSerializer):
    """
    Serializer for folder model.
    """
    id = custom_fields.IdencodeField(read_only=True)
    created_on = serializers.DateTimeField(
        read_only=True,format='%d-%m-%Y')

    class Meta:
        """
        Meta info.
        """
        model = node_models.Folder
        fields = ('id','name','created_on',)

    def validate(self, attrs):
        """
        Validation overrided to avoid repeated folder name under same node.
        """
        folders = node_models.Folder.objects.filter(
            node=session.get_current_node(),
            name__iexact=attrs['name'],is_deleted=False)
        if folders.exists():
            raise exceptions.BadRequest(_("Folder already exists"))
        return super().validate(attrs)

    def create(self, validated_data):
        """
        Create overrided to add node into the folder.
        """
        validated_data['node'] = session.get_current_node()
        return super().create(validated_data)
