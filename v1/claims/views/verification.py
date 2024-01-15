"""Views related to claim verification"""

from rest_framework import generics

from django.db.models import Q

from base.views import IdDecodeModelViewSet
from base import session

from v1.claims import models as claim_models
from v1.claims.serializers import verification as verif_serializers
from v1.claims import filters as claim_filters


class ClaimVerificationViewSet(IdDecodeModelViewSet):
    """
    View to create, list and update claims.
    """

    http_method_names = ['get',]
    filterset_class = claim_filters.VerificationFilter
    
    def get_queryset(self):
        """Overrided queryset to list claims under specific tenant"""
        node = session.get_current_node()
        queryset = claim_models.AttachedClaim.objects.none()
        if session.get_current_tenant().node_claim:
            queryset |= claim_models.AttachedClaim.objects.filter(
                claim__attach_to_node=True, verifier=node)
        if session.get_current_tenant().batch_claim:
            queryset |= claim_models.AttachedClaim.objects.filter(
                claim__attach_to_batch=True, verifier=node)
        if session.get_current_tenant().connection_claim:
            queryset |= claim_models.AttachedClaim.objects.filter(
                claim__attach_while_connecting=True, verifier=node)
        return queryset.order_by('status', '-created_on')

    def get_serializer_class(self, *args, **kwargs):
        """Serializers changed with respect to request method"""
        serializer = verif_serializers.VerificationSerializer
        if self.action == 'list':
            serializer = verif_serializers.VerificationListSerializer
        return serializer


class VerifyClaimView(generics.UpdateAPIView):
    """
    View verify attached claim.
    """

    permission_classes = []
    serializer_class = verif_serializers.VerificationSerializer
    
    def get_queryset(self):
        """Overrided queryset to list claims under specific node"""
        node = session.get_current_node()
        return claim_models.AttachedClaim.objects.filter(
            verifier=node)
