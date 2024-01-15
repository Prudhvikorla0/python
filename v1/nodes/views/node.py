
from rest_framework import generics
from rest_framework import filters
from rest_framework.views import APIView

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _

from base import session
from base.views import IdDecodeModelViewSet
from base import exceptions as base_exceptions
from base.response import SuccessResponse
from utilities.functions import decode

from v1.tenants import constants as tenant_constants
from v1.tenants import models as tenant_models

from v1.nodes.serializers import node as node_serializers
from v1.nodes import models as node_models
from v1.nodes import filters as node_filters
from v1.nodes import constants as node_consts

from v1.accounts import constants as user_consts

from v1.risk.integrations.roai import apis as roai_apis

# from v1.apiauth import permissions as auth_permissions
from v1.risk.integrations.roai import apis as roai_apis


class NodeRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    """

    serializer_class = node_serializers.NodeSerializer

    def get_queryset(self):
        """
        """
        if self.request.method == 'PATCH':
            current_node = session.get_current_node()
            query = Q(
                status=node_consts.NodeStatus.INACTIVE,
                invited_by=current_node)
            query |= Q(id=current_node.id)
            return node_models.Node.objects.filter(query)
        tenant = session.get_current_tenant()
        return node_models.Node.objects.filter(tenant=tenant)


class NodeDocumentViewSet(IdDecodeModelViewSet):
    """
    """

    filterset_class = node_filters.NodeDocumentFilter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name',]
    serializer_class = node_serializers.NodeDocumentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete',]

    def get_serializer_class(self):
        """
        Return appropirate serializer.
        """
        if self.action == 'list':
            return node_serializers.NodeDocumentBaseSerializer
        return node_serializers.NodeDocumentSerializer

    def get_queryset(self):
        """
        """
        node = session.get_current_node()
        documents = node_models.NodeDocument.objects.filter(
            node=node, is_deleted=False).select_related(
            'node', 'category').order_by('-created_on')
        return documents

    def destroy(self, request, *args, **kwargs):
        """
        Destroy overrided to check node of the user and document are same.
        """
        node = session.get_current_node()
        document = self.get_object()
        if document.node != node:
            raise base_exceptions.BadRequest(_("Document can not be deleted."))
        document.is_deleted = True
        document.save()
        return SuccessResponse(_("Document deleted successfully."))


class NodeMemberViewSet(IdDecodeModelViewSet):
    """
    """

    filterset_class = node_filters.NodeMemberFilter
    serializer_class = node_serializers.NodeMemberSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['user__first_name', 'user__last_name']
    http_method_names = ['get', 'post', 'patch', 'delete',]

    def get_queryset(self):
        """
        """
        node = session.get_current_node()
        members = node_models.NodeMember.objects.filter(
            node=node, is_active=True).select_related(
            'default_supply_chain', 'user').order_by('-created_on')
        return members

    def destroy(self, request, *args, **kwargs):
        """
        Destroy overrided to delete node member and
        to remove the default node of the user if the default node is the
        node member's node.
        """
        node = session.get_current_node()
        member = self.get_object()
        if member.type == node_consts.NodeMemberType.SUPER_ADMIN:
            raise base_exceptions.BadRequest(
                _("Can not remove super admin admin."))
        if member.user.default_node == node:
            member.user.default_node = None
            member.user.save()
        member.delete()
        return SuccessResponse(_("Member deleted successfully."))


class ResendNodeMemberInvite(APIView):
    """Resend invite to node member."""

    def post(self, request, *args, **kwargs):
        """
        Post overrided to resend invite to a node member.
        """
        id = decode(self.request.data.get('id', None))
        try:
            nodemember = node_models.NodeMember.objects.get(
                id=id, node=session.get_current_node(),
                user__status=user_consts.UserStatus.CREATED)
        except:
            raise base_exceptions.BadRequest(
                _("Node member does not exist"))
        nodemember.send_invite()
        return SuccessResponse(_("Resend successfully"))


class SearchNode(generics.ListAPIView):
    """Resend invite to node member."""

    serializer_class = node_serializers.BasicNodeSerializer
    filterset_class = node_filters.NodeFilter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']

    def get_queryset(self):
        """
        Returns a filtered queryset of nodes based on certain conditions.

        The queryset can be filtered based on the current tenant's node discoverability preferences,
        whether the node is discoverable or not, and whether
        the current node should be included in the results or not.

        Returns:
        - A queryset of nodes that match the specified conditions.
        """
        tenant = session.get_current_tenant()
        connect_id = self.request.query_params.get('connect_id', None)
        include_current_node = self.request.query_params.get('include_current_node', False)
        if tenant.node_discoverability == tenant_constants.DiscoverabilityType.ALWAYS:
            # All nodes are Discoverable
            queryset = node_models.Node.objects.all()
        elif tenant.node_discoverability == tenant_constants.DiscoverabilityType.NODE_PREFERENCE:
            # Can search discoverable nodes or is a connect-ID is mention,
            # that node is also discoverable.
            queryset = node_models.Node.objects.filter(
                Q(is_discoverable=True) | Q(connect_id=connect_id))
        elif tenant.node_discoverability == tenant_constants.DiscoverabilityType.HIDDEN:
            # Can search only with Connect-ID
            queryset = node_models.Node.objects.filter(connect_id=connect_id)
        else:
            queryset = node_models.Node.objects.none()
        if not include_current_node:
            # To be used for connecting to existing companies.
            curr_node = session.get_current_node()
            queryset = queryset.exclude(id=curr_node.id)
        return queryset.filter(tenant=tenant)


class ROAINodeSearch(APIView):
    """
    Api to get nodes from ro and ro-ai and returns as a list.
    """

    def get(self, request, *args, **kwargs):
        """
        """
        search = request.query_params.get('search', '')
        type = request.query_params.get('type', None)
        limit = int(request.query_params.get('limit', 10))
        offset = int(request.query_params.get('offset', 0))
        supply_chain = decode(
            request.query_params.get('supply_chain', None))
        ai_nodes = roai_apis.NodeSearch().call(
            search=search,limit=limit,offset=offset)
        tenant = session.get_current_tenant()
        current_node = session.get_current_node()
        current_node_connections = current_node.get_connection_circle(
            sc=supply_chain).values_list('id',flat=True)
        existing_nodes = node_models.Node.objects.filter(
            tenant=tenant,name__icontains=search)
        nodes = existing_nodes.exclude(
            id__in=current_node_connections)
        data = node_serializers.BasicNodeSerializer(nodes, many=True).data
        for ai_node in ai_nodes:
            node_exists = existing_nodes.filter(
                name=ai_node['name'],
                province__name=ai_node['address']['state']
                ).exists()
            if node_exists:
                continue
            try:
                province = tenant_models.Province.objects.filter(
                    name=ai_node['address']['state']).first()
                country = {
                    "id": province.country.idencode,
                    "name": province.country.name
                    }
                province = {
                    "id": province.idencode,
                    "name": province.name
                    }
            except:
                country = ''
                province = ''
            ai_node_data = {
                "id": "", 
                "name": ai_node['name'],
                "country": country,
                "province": province
            }
            data.append(ai_node_data)
        return SuccessResponse(data[:limit],default_data=[])
