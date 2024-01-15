"""URLs of the app tenants."""

from rest_framework import routers
from django.urls import path

from v1.risk.views import certifications as cert_views

router = routers.SimpleRouter()

urlpatterns = router.urls

urlpatterns += [
    path('certifications/recommended/',
         cert_views.RecommendedCertificationsView.as_view()),
    path('certifications/<idencode:node_id>/recommended/',
         cert_views.RecommendedCertificationsView.as_view()),
    path('certifications/',
         cert_views.ListNodeCertificationsView.as_view()),
    path('certifications/<idencode:node_id>/',
         cert_views.ListNodeCertificationsView.as_view()),
]
