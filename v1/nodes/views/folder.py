"""APIS related to folder"""
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from base.views import IdDecodeModelViewSet
from base import session
from base import response

from v1.nodes import models as node_models
from v1.nodes.serializers import folder as folder_serializer
from v1.nodes import filters as node_filters


class FolderViewSet(IdDecodeModelViewSet):
    """
    Api to create,list,update and delete folder.
    """
    filterset_class = node_filters.FolderFilter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name',]
    serializer_class = folder_serializer.FolderSerializer

    def get_queryset(self):
        """
        Return folders under the current node
        """
        folders = node_models.Folder.objects.filter(
            node=session.get_current_node(),is_deleted=False
            ).order_by('-created_on')
        return folders
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete overrided to make the delete boolean true.
        """
        folder = self.get_object()
        folder.is_deleted = True
        folder.documents.update(is_deleted=True)
        folder.save()
        return response.SuccessResponse("Folder deleted successfully")
