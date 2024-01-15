"""Serializers for dynamic forms."""
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from rest_framework import serializers

from base import exceptions as base_exceptions
from base import session
from utilities import mongo_functions

from common.drf_custom import fields as custom_fields
from utilities import functions as util_functions

from v1.dynamic_forms import models as form_models
from v1.dynamic_forms import constants as form_consts

from v1.nodes import models as node_models


class FieldValueOptionSerializer(serializers.ModelSerializer):
    """
    Serializer for options for the field values.
    These options are used with the field types of the category selection.
    """
    id = custom_fields.IdencodeField(read_only=True)
    
    class Meta:
        """
        Meta Info.
        """

        model = form_models.FieldValueOption
        fields = ('id', 'name', 'is_default',)


class FormFieldSerializer(serializers.ModelSerializer):
    """
    Serializer to create and list fields for dynamic forms.
    """
    field = custom_fields.IdencodeField(read_only=True, source='id')
    file = serializers.FileField(required=False)
    options = FieldValueOptionSerializer(
        many=True, required=False)
    form = custom_fields.IdencodeField(
        related_model=form_models.Form, required=False, 
        allow_null=True)

    class Meta:
        """
        Meta Info.
        """
        model = form_models.FormField
        exclude = (
            'id', 'creator', 'updater', 'created_on', 'updated_on', )

    def create_options(self, options_data, field):
        """Method to create options."""
        current_user = session.get_current_user()
        tenant = session.get_current_tenant()
        for option_data in options_data:
            option_data['creator'] = current_user.id
            option_data['updater'] = current_user.id
            option_data['tenant'] = tenant.id
            option = FieldValueOptionSerializer(data=option_data)
            if not option.is_valid():
                base_exceptions.BadRequest(_("Option validation failed"))
            option = option.save()
            field.options.add(option)
            return True

    def create(self, validated_data):
        """
        Create overrided to add options
        """
        current_user = session.get_current_user()
        validated_data['creator'] = current_user
        validated_data['updater'] = current_user
        options = validated_data.pop('options', None)
        field = super().create(validated_data)
        if options:
            self.create_options(options, field)
        return field


class EmptyFieldValueSerializer(serializers.ModelSerializer):
    """
    Serializer list fields with empty values.
    """
    field = custom_fields.IdencodeField(read_only=True, source='id')

    class Meta:
        """
        Meta Info.
        """
        model = form_models.FormField
        fields = ('field',)

    def to_representation(self, instance):
        """
        To representation overrided to add extra data.
        """
        data=  super().to_representation(instance)
        data['value'] = ''
        data['file'] = None
        data['selected_options'] = []
        return data


class FormSerializer(serializers.ModelSerializer):
    """
    Serializer to create and view details of a dynamic form.
    """

    id = custom_fields.IdencodeField(read_only=True)
    fields = FormFieldSerializer(many=True)

    class Meta:
        """
        Meta Info.
        """
        model = form_models.Form
        exclude = ('creator', 'updater', 'created_on', 'updated_on',)


class FieldValueSerializer(serializers.ModelSerializer):
    """
    Serializer to list and create field values under a submitted form.
    """
    field = custom_fields.IdencodeField(
        related_model=form_models.FormField, required=False)
    form = custom_fields.IdencodeField(
        write_only=True, related_model=form_models.FormSubmission)
    submission_form_mongo_id = serializers.CharField(required=False)
    type = serializers.IntegerField(source='field.type', read_only=True)
    label = serializers.CharField(source='field.label', read_only=True)
    placeholder = serializers.CharField(
        source='field.place_holder', read_only=True)
    info = serializers.CharField(source='field.info', read_only=True)
    key = serializers.CharField(source='field.key', read_only=True)
    position = serializers.CharField(source='field.position', read_only=True)
    required = serializers.CharField(source='field.required', read_only=True)
    options = FieldValueOptionSerializer(
        source='field.options', many=True, read_only=True)
    selected_options = custom_fields.ManyToManyIdencodeField(
        related_model=form_models.FieldValueOption, required=False)
    width = serializers.IntegerField(source='field.width', read_only=True)
    company_document = custom_fields.IdencodeField(
        required=False, related_model=node_models.NodeDocument)
    is_delete = serializers.BooleanField(default=False, required=False)

    class Meta:
        """
        Meta Info.
        """
        model = form_models.FormFieldValue
        fields = (
            'field', 'type', 'label', 'placeholder', 'info', 'key', 
            'position', 'required', 'options', 'value', 'file', 'form', 
            'selected_options', 'width', 'company_document', 'files', 
            'submission_form_mongo_id', 'is_delete',
            )

    def create(self, validated_data):
        """
        Create overrided.

        Current user is assigned to cretor and updater fields.
        Fieldvalue get or create query called after that the object is 
        populated with the provided data.
        """
        field = validated_data.pop('field')
        form = validated_data.pop('form')
        if 'file' in validated_data and validated_data['file']:
            validated_data['file_hash'] = util_functions.hash_file(validated_data['file'])
        value, created = form_models.FormFieldValue.objects.get_or_create(
            field=field, form=form)
        if validated_data.pop('is_delete',False):
            value.file = None
            value.value = ''
            value.save()
            value.selected_options.set([])
        data = super().update(value, validated_data)
        return data


class FormSubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer to create submission form.
    """

    id = custom_fields.IdencodeField(read_only=True)
    form = custom_fields.IdencodeField( 
        related_model=form_models.Form, write_only=True)
    mongo_submission_id = serializers.CharField(read_only=True)

    class Meta:
        """
        Meta Info.
        """
        model = form_models.FormSubmission
        fields = ('id','form', 'mongo_submission_id')

    def create(self, validated_data):
        """
        Create overrided to create submission form in mongoDB.
        And the created mongodb instance id assigned into the
        mongo_submission_id key in the created submission form.
        """
        submission_form = super().create(validated_data)
        mongo_dict = {
            '_meta' : {
                "submission_form":submission_form.idencode, 
                "form": submission_form.form.idencode
                }
        }
        # mongo_instance = mongo_functions.add_single_document(
        #     form_consts.FORM_SUBMISSION_MONGO,mongo_dict)
        # submission_form.mongo_submission_id = mongo_instance
        # submission_form.save()
        return submission_form


class FieldValueUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer to update the fieldvalues.
    This serializer is implimented mainly to add files to the dynamic form.
    """
    file = serializers.FileField(required=False, write_only=True)
    form = custom_fields.IdencodeField(
        related_model=form_models.FormSubmission, write_only=True, 
        required=False)
    value = serializers.CharField(required=False, write_only=True)
    selected_options = custom_fields.ManyToManyIdencodeField(
        related_model=form_models.FieldValueOption, required=False, 
        write_only=True)
    company_document = custom_fields.IdencodeField(
        required=False, related_model=node_models.NodeDocument)
    is_delete = serializers.BooleanField(default=False, required=False)

    class Meta:
        """
        Meta Info.
        """
        model = form_models.FormField
        fields = (
            'file', 'value', 'selected_options', 'form', 'company_document', 
            'is_delete',)

    def update(self, instance, validated_data):
        """
        Update method overrided.
        field and updater fields are populated at here.
        FieldValueSerializer called to create / update the field values.
        """
        validated_data['field'] = instance
        is_delete = validated_data.get('is_delete', False)
        serializer = FieldValueSerializer(data=validated_data)
        if not serializer.is_valid(raise_exception=True):
            raise base_exceptions.BadRequest(_("Field Updation Failed !"))
        field_value = serializer.save()
        # update_data = {f"{instance.key}": ""}
        # if not is_delete:
        #     update_data = {f"{instance.key}": field_value.file.url}
        # if instance.type != form_consts.FieldType.FILE:
        #     update_data = {f"{instance.key}": validated_data.get(
        #         'value', validated_data.get('selected_options'))}
        # mongo_functions.update_single_document(
        #     form_consts.FORM_SUBMISSION_MONGO, 
        #     validated_data['form'].mongo_submission_id, update_data)
        return instance
