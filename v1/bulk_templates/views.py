"""
Views for bulk templates
"""
from drf_yasg.utils import swagger_auto_schema

from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.query_utils import Q
from django.db.models.functions import Length
from rest_framework import views
from rest_framework import generics
from rest_framework import parsers
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from base import session
from base import views
from base import exceptions
from base import response
from base import swagger

from v1.supply_chains.models import SupplyChain

from . import models as bulk_models
from . import serializers
from . import constants
from . import filters as bulk_filters

import openpyxl
from sentry_sdk import capture_exception


class DownloadTemplateView(views.APIView):
    """
    API to download the template Excel file.
    """
    http_method_names = ['get']

    @swagger_auto_schema(
        manual_parameters=swagger.add_query_params(
            'type', 'supply_chain', 'limit'))
    def get(self, request, *args, **kwargs):
        node = session.get_current_node()
        sc_id = request.query_params.get('supply_chain')
        ttype = request.query_params.get('type')
        limit = request.query_params.get('limit', None)
        template_id = request.query_params.get('template_id', None)
        supply_chain = SupplyChain.objects.get_by_encoded_id(sc_id)
        tenant = session.get_current_tenant()
        template = bulk_models.Template.get_tenant_template(
            template_type=ttype, tenant=tenant, id=template_id)
        if limit:
            if not limit.isdigit() or int(limit) < 1:
                raise ValueError('Limit must be a positive integer.')
            if int(limit) > 50000:
                raise ValueError('Maximum limit supported is 50000')
            template.item_count = int(limit)
        file = template.get_template_file(supply_chain, tenant, node)
        file_name = template.get_file_name()
        response = HttpResponse(
            file,
            content_type="application/vnd.openxmlformats" +
                         "-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response


class BulkUploadViewset(views.IdDecodeModelViewSet):
    """
    API to validate a template

    API lets you upload a template to validate the rows in it.
    """

    http_method_names = ['get', 'post', 'patch']
    # parser_classes = (parsers.MultiPartParser, parsers.JSONParser)
    # parser_classes = (parsers.MultiPartParser,)

    filterset_class = bulk_filters.BulkUploadFilter

    def get_serializer_class(self):
        if self.action in ['retrieve', 'create', 'partial_update']:
            return serializers.BulkUploadSerializer
        return serializers.BulkUploadListSerializer

    def get_queryset(self):
        """
        """
        node = session.get_current_node()
        return bulk_models.BulkUpload.objects.filter(
            node=node).exclude(status=constants.BulkUploadStatuses.CREATED)


class InitiateBulkUpload(APIView):
    """API to initiate Bulk upload."""

    def post(self, request, *args, **kwargs):
        """
        Post overrode to initial bulk upload.
        """
        try:
            bulk_upload = bulk_models.BulkUpload.objects.get(
                id=self.kwargs.get('pk', -1)
            )
        except Exception as e:
            raise exceptions.BadRequest(_("Invalid Bulk Upload. Check the ID."))
        bulk_upload.start_upload()
        return response.SuccessResponse(_("Bulk upload started successfully."))


class TemplateFieldsViewset(generics.ListAPIView):
    """API to get fields for the template and their respective details like
    label, placeholder, list of countries for dropdown etc"""

    serializer_class = serializers.TemplateFieldsSerializer

    def get_queryset(self):
        """
        Return fields ordered by column position with respect to the 
        template id passed in the queryparams.
        """

        return bulk_models.TemplateField.objects.filter(
            template=self.kwargs.get('pk')).annotate(
                length=Length('column_pos')).order_by(
                    'length', 'column_pos')


class TemplateListView(generics.ListAPIView):
    """API to list all the templates under the tenant"""

    serializer_class = serializers.TemplateSerializer
    filterset_class = bulk_filters.TemplateFilter

    def get_queryset(self):
        tenant = session.get_current_tenant()
        templates = bulk_models.Template.objects.filter(
            Q(tenant=tenant) | Q(tenant=None)).select_related('tenant')
        return templates


class TemplateCheckView(APIView):
    """API to return columns for the template and to validate the type of 
    template"""
    
    def post(self, request, format=None):
        file = request.data['file']
        try:
            wb = openpyxl.load_workbook(file, data_only=True)
        except Exception as e:
            capture_exception(e)
            raise exceptions.BadRequest(_("Unrecognized file."))

        file_name = request.data['file_name']
        name = request.data['name']
        template = bulk_models.Template.objects.create(
            file=file, file_name=file_name, name=name)

        active_sheet = wb.active
        columns = []
        for column in active_sheet:
            for cell in column:
                if cell.value:
                    if cell.column_letter not in columns:
                        columns.append(cell.column_letter)
        
        type = request.data['type']
        field_types = bulk_models.TemplateFieldType.objects.filter(
            template_type=type).values('key', 'required', 'name', 'placeholder',
            'description', 'width', 'type')
        data = {
            'columns': columns,
            'field_types': field_types,
            'template': template.idencode
        }
        return Response(data, status=status.HTTP_200_OK)


class CustomTemplateView(generics.CreateAPIView):
    """API to create templates under the tenant"""

    serializer_class = serializers.TemplateSerializer
    queryset = bulk_models.Template.objects.all()