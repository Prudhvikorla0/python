"""Views related to claim"""

from base.views import IdDecodeModelViewSet
from base import session
from base import exceptions
from base.response import SuccessResponse

from utilities.functions import decode

from rest_framework import generics
from rest_framework import filters
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend

from v1.claims import models as claim_models
from v1.claims.serializers import claim as claim_serializers
from v1.claims.serializers import node_claims as node_claim_serializers
from v1.claims.serializers import batch_claim as batch_claim_serializers
from v1.claims.serializers import connection_claim as conn_claim_serializers
from v1.claims import filters as claim_filters
from v1.claims.utilities import expire_claims # TODO: temporary fix.


class ClaimViewSet(IdDecodeModelViewSet):
    """
    View to create, list and update claims.
    """

    http_method_names = ['get', 'post', 'patch']
    filterset_class = claim_filters.ClaimFilter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name',]
    serializer_class = claim_serializers.ClaimSerializer
    

    def get_queryset(self):
        """Overrided queryset to list claims under specific tenant"""
        tenant = session.get_current_tenant()
        return claim_models.Claim.objects.filter(
            tenant=tenant, is_active=True).prefetch_related(
            'supply_chains', 'verifiers', 'criteria')


class CriterionViewSet(IdDecodeModelViewSet):
    """
    View to create and update criterion.
    """

    http_method_names = ['post', 'patch',]
    serializer_class = claim_serializers.CriterionSerializer
    

    def get_queryset(self):
        """
        Overrided queryset to list claims under specific tenant
        """
        tenant = session.get_current_tenant()
        return claim_models.Criterion.objects.filter(
            claim__tenant=tenant, claim__is_active=True)


class NodeClaimViewSet(IdDecodeModelViewSet):
    """
    View to create, list, retrieve and delete company claims.
    """

    http_method_names = ['post', 'get', 'delete']
    filter_backends = [filters.SearchFilter,]
    search_fields = ['claim__name',]
    serializer_class = node_claim_serializers.NodeClaimSerializer

    def get_queryset(self):
        """
        Overrided queryset to list company claims.
        """
        node_id = self.request.query_params.get(
            'node', session.get_current_node().idencode)
        node = decode(node_id)
        expire_claims(session.get_current_tenant())
        return claim_models.NodeClaim.objects.filter(node__id=node).select_related(
            'node')


class ConnectionClaimViewSet(IdDecodeModelViewSet):
    """
    View to create, list, retrieve and delete company claims.
    """

    http_method_names = ['post', 'get', 'delete']
    filter_backends = [filters.SearchFilter,]
    search_fields = ['claim__name',]
    serializer_class = conn_claim_serializers.ConnectionClaimSerializer

    def get_queryset(self):
        """
        Overrided queryset to list company claims.
        """
        connection_id = self.request.query_params.get(
            'connection', session.get_current_node().idencode)
        return claim_models.ConnectionClaim.objects.filter(
            connection__id=decode(connection_id)).select_related(
            'connection')


class BatchClaimViewSet(IdDecodeModelViewSet):
    """
    View to create, list, retrieve and delete batch claims.
    """

    http_method_names = ['post', 'get', 'delete']

    def get_serializer_class(self, *args, **kwargs):
        """Serializers changed with respect to request method"""
        serializer = batch_claim_serializers.BatchClaimSerializer
        if self.request.method == 'POST':
            serializer = batch_claim_serializers.AttachBatchClaimSerializer
        return serializer

    def get_queryset(self):
        """
        Overrided queryset to list batch claims.
        """
        node = session.get_current_node()
        return claim_models.BatchClaim.objects.filter(batch__node=node).select_related(
            'batch', 'transaction', 'verifier', 'attached_by', 'claim').prefetch_related(
            'criteria')


class GetInheritableClaims(generics.CreateAPIView):
    """
    View to verify which claims can be inherited in a list of batches
    """

    serializer_class = claim_serializers.InheritableClaimSerializer


class AttachedClaimCommentCreateListView(generics.ListCreateAPIView):
    """
    Viewset to create, list, update and delete claim comment.
    """

    serializer_class = claim_serializers.AttachedClaimCommentSerializer

    def get_queryset(self):
        """
        Return comments with respect to the id passed in the queryparams.
        """
        claim_id = self.kwargs['id']
        comments = claim_models.AttachedClaimComment.objects.filter(
            attached_claim__id=claim_id).select_related(
            'creator', 'updater', 'company_document').order_by('-created_on')
        return comments


class AttachedClaimCommentRetrieveView(generics.RetrieveDestroyAPIView):
    """
    Viewset to create, list, update and delete claim comment.
    """

    serializer_class = claim_serializers.AttachedClaimCommentSerializer

    def get_object(self):
        """
        Return comments with respect to the id passed in the queryparams.
        """
        comment_id = self.kwargs['pk']
        try:
            comments = claim_models.AttachedClaimComment.objects.get(
                id=comment_id)
        except:
            raise exceptions.NotFound(_("Comment does not exist."))
        return comments

    def destroy(self, request, *args, **kwargs):
        """
        Destroy overrided to delete attached comment by checking 
        logged-in user's type. 
        """
        comment = self.get_object()
        member = session.get_current_node().node_members.get(
            user=session.get_current_user())
        if member != comment.member:
            raise exceptions.BadRequest(_("User can not remove the comment"))
        comment.delete()
        return SuccessResponse(_("Comment deleted successfully."))


class AttachedClaimView(generics.ListAPIView):
    """
    Common API to list all attached claims.
    Here we use connection, node, batch parameters to add 
    specific node's, connection's and batch's claims.
    """

    serializer_class = claim_serializers.BaseAttachedClaimSerializer

    def get_queryset(self):
        """
        Queryset overrided to add filters.
        """
        connection = self.request.query_params.get(
            'connection', None)
        node = self.request.query_params.get(
            'node', None)
        batch = self.request.query_params.get(
            'batch', None)
        attached_claims = claim_models.AttachedClaim.objects.all()
        claims = claim_models.AttachedClaim.objects.none()
        if connection:
            connection_claims = attached_claims.filter(
                connectionclaim__connection__id=decode(connection))
            claims |= connection_claims
        if node:
            node_claims = attached_claims.filter(
                nodeclaim__node__id=decode(node))
            claims |= node_claims
        if batch:
            batch_claims = attached_claims.filter(
                batchclaim__batch__id=decode(batch))
            claims |= batch_claims
        return claims.distinct()
