"""Views for the form related apis are stored here."""

from base.views import IdDecodeModelViewSet
from base import session
from base import exceptions as base_exceptions
from utilities import mongo_functions

from rest_framework.views import APIView
from rest_framework import generics

from base.response import SuccessResponse

from v1.dynamic_forms.serializers import form as form_serializers
from v1.dynamic_forms import models as form_models
from v1.dynamic_forms import constants as form_consts


class FormViewSet(IdDecodeModelViewSet):
    """
    Viewset for form related activities.
    """

    http_method_names = ['get',]
    serializer_class = form_serializers.FormSerializer
    queryset = form_models.Form.objects.all().prefetch_related('fields')


class FormSubmissionCreateView(generics.CreateAPIView):
    """
    View to create submission form.
    Submission form is the form between the fields , fieldvalues and 
    fieldvalue related model.
    """

    serializer_class = form_serializers.FormSubmissionSerializer


class FormSubmissionView(APIView):
    """
    View to get the field values under a submitted form and
    to add or update fieldvalues.
    """

    def get(self, request, *args, **kwargs):
        """
        Get method is overrided.
        if there is no fieldvalues FormFieldSerializer called,
        else the FieldValueSerializer is called.
        """
        form = form_models.FormSubmission.objects.get(
                    id=self.kwargs['pk'])
        if not form.field_values.exists():
            data = form_serializers.EmptyFieldValueSerializer(
                form.form.fields.all(), many=True).data
        else:
            data = form_serializers.FieldValueSerializer(
                form.field_values.all(), many=True).data
        return SuccessResponse(data)

    def post(self, request, *args, **kwargs):
        """
        Post method is overrided.
        The list of field data looped and FieldValueSerializer is called to
        create or update the field values.
        """
        data = request.data
        form = form_models.FormSubmission.objects.get(
            id=self.kwargs['pk'])
        for data_value in data:
            data_value['form'] = form
            serializer = form_serializers.FieldValueSerializer(
                data=data_value)
            if not serializer.is_valid(raise_exception=True):
                raise base_exceptions.BadRequest("Form Submission Failed")
            serializer.save()
        # if not form.mongo_submission_id:
        #     mongo_dict = {
        #     '_meta' : {
        #         "submission_form":form.idencode, 
        #         "form": form.form.idencode
        #         }
        #         }
        #     mongo_instance = mongo_functions.add_single_document(
        #         form_consts.FORM_SUBMISSION_MONGO,mongo_dict)
        #     form.mongo_submission_id = mongo_instance
        #     form.save()
        # mongo_functions.update_single_document(
        #     form_consts.FORM_SUBMISSION_MONGO, form.mongo_submission_id,
        #     form.export_as_dict())
        return SuccessResponse("Form Updated Successfully")


class FieldValueUpdateView(generics.UpdateAPIView):
    """
    View to update / create single field value.
    """

    serializer_class = form_serializers.FieldValueUpdateSerializer

    def get_object(self):
        """
        Get object method is overrided to return check field come under 
        the user's tenant.
        """
        field_id = self.kwargs['pk']
        tenant = session.get_current_tenant()
        try:
            field = form_models.FormField.objects.get(id=field_id)
        except:
            raise base_exceptions("Field Doesn't exist.")
        return field
