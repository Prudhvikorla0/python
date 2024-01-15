from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

from common.drf_custom import fields as custom_fields
from base import session
from base import exceptions

from v1.transactions import models as txn_models

from v1.accounts.serializers.user import BasicUserSerializer

from v1.nodes.models import NodeMember, NodeDocument
from v1.nodes.serializers import node as node_serializers
from v1.nodes.constants import NodeMemberType


class TransactionCommentSerializer(serializers.ModelSerializer):
    """Serializer for transaction comment."""

    id = custom_fields.IdencodeField(read_only=True)
    creator = custom_fields.IdencodeField(
        serializer=BasicUserSerializer, read_only=True)
    updater = custom_fields.IdencodeField(
        serializer=BasicUserSerializer, read_only=True)
    created_on = custom_fields.UnixDateField(read_only=True)
    updated_on = custom_fields.UnixDateField(read_only=True)
    company_document = custom_fields.IdencodeField(
        required=False, related_model=NodeDocument)

    class Meta:
        """
        Meta Info.
        """

        model = txn_models.TransactionComment
        fields = (
            'id', 'comment', 'file', 'name', 'creator' , 'updater', 
            'created_on', 'updated_on', 'extra_info', 'company_document', 
        )

    def create(self, validated_data):
        """
        Overrided create to add creator and updater.
        """
        company_document = validated_data.get('company_document', None)
        if company_document:
            validated_data['file'] = company_document.file
            validated_data['name'] = company_document.name
        current_user = session.get_current_user()
        validated_data['member'] = session.get_current_node().node_members.get(
            user=current_user)
        try:
            transaction = txn_models.Transaction.objects.get(
                id=self.context.get('view').kwargs.get('id', None))
        except:
            raise exceptions.NotFound(_("Transaction does not exist"))
        validated_data['transaction'] = transaction
        comment = super().create(validated_data)
        comment.notify()
        return comment

    def update(self, instance, validated_data):
        """
        Checks the updater is the owner or admin.
        Assign user into updater.
        """
        company_document = validated_data.get('company_document', None)
        if company_document:
            validated_data['file'] = company_document.file
            validated_data['name'] = company_document.name
        current_user = session.get_current_user()
        company_document = validated_data.get(
            'company_document', None)
        if company_document:
            validated_data['file'] = company_document.file
            validated_data['name'] = company_document.name
        node_user = NodeMember.objects.get(user=current_user)
        if current_user != instance.creator and \
            node_user.type != NodeMemberType.ADMIN:
            raise exceptions.AccessForbidden(
                _("User is not allowed to edit comment."))
        return super().update(instance, validated_data)
