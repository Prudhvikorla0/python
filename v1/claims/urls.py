"""URLs of the app claims."""

from rest_framework import routers

from django.urls import path

from v1.claims import models as claim_models
from v1.claims.views import claim as claim_viewset
from v1.claims.views import verification as verif_viewset


router = routers.SimpleRouter()

urlpatterns = [
    path('inheritable/', claim_viewset.GetInheritableClaims.as_view()), 
    path('verification/<idencode:pk>:verify', 
        verif_viewset.VerifyClaimView.as_view()), 
    path('attached/<idencode:id>/comment/', 
        claim_viewset.AttachedClaimCommentCreateListView.as_view()), 
    path('attached/comment/<idencode:pk>/', 
        claim_viewset.AttachedClaimCommentRetrieveView.as_view()),
    path('attached/', 
        claim_viewset.AttachedClaimView.as_view()),
]

router.register(r'criterion', claim_viewset.CriterionViewSet, 
basename=claim_models.Criterion)
router.register(r'company', claim_viewset.NodeClaimViewSet,
basename=claim_models.NodeClaim)
router.register(r'connection', claim_viewset.ConnectionClaimViewSet,
basename=claim_models.ConnectionClaim)
router.register(r'batch', claim_viewset.BatchClaimViewSet, 
basename=claim_models.BatchClaim)
router.register(r'verification', verif_viewset.ClaimVerificationViewSet, 
basename=claim_models.AttachedClaim)
router.register(r'', claim_viewset.ClaimViewSet, 
    basename=claim_models.Claim)


urlpatterns += router.urls

