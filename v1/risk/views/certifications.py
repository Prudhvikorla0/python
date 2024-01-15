"""
Customizations for API views
"""
import re
from collections import defaultdict as dd
from drf_yasg.utils import swagger_auto_schema

from django.db import models
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from base import session
from base.response import SuccessResponse
from base import swagger
from utilities.functions import decode
from v1.nodes import models as node_models


class RecommendedCertificationsView(APIView):

    @swagger_auto_schema(
        manual_parameters=swagger.add_query_params(
            'limit', 'offset'))
    def get(self, request, *args, **kwargs):
        current_node = session.get_current_node()
        if 'node_id' in kwargs:
            try:
                current_node = node_models.Node.objects.get(
                    id=kwargs['node_id'])
            except:
                return Response({"error": "Node not found"}, status=status.HTTP_404_NOT_FOUND)
        limit = request.query_params.get('limit', 100)
        offset = request.query_params.get('offset', 0)

        certifications = current_node.get_recommended_certifications(
            limit=limit, offset=offset)

        return SuccessResponse(certifications)


class ListNodeCertificationsView(APIView):

    @swagger_auto_schema(
        manual_parameters=swagger.add_query_params(
            'limit', 'offset'))
    def get(self, request, *args, **kwargs):

        current_node = session.get_current_node()
        if 'node_id' in kwargs:
            try:
                current_node = node_models.Node.objects.get(
                    id=kwargs['node_id'])
            except:
                return Response({"error": "Node not found"}, status=status.HTTP_404_NOT_FOUND)

        limit = request.query_params.get('limit', 100)
        offset = request.query_params.get('offset', 0)

        data = current_node.get_added_certifications(
            limit=limit, offset=offset)

        if 'certifications' in data:
            return SuccessResponse(data['certifications'])

        return SuccessResponse([])
