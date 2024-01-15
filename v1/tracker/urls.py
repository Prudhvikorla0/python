"""URLs of the app tenants."""

from rest_framework import routers
from django.urls import path

from v1.tracker.views import tracker as tracker_views

router = routers.SimpleRouter()

urlpatterns = router.urls

urlpatterns += [
    path('batch/<idencode:pk>/track/', tracker_views.TrackBatchFlowView.as_view()), 
    path('batch/<idencode:pk>/', tracker_views.BatchDetailView.as_view()), 
    path('batch/<idencode:pk>/info/', tracker_views.TrackerInfoView.as_view()),
]
