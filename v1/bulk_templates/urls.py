"""URLs of the app supply-chains."""

from rest_framework import routers
from django.urls import path

from . import models as bulk_models

from v1.bulk_templates import views

router = routers.SimpleRouter()
router.register(r'uploads', views.BulkUploadViewset,
    basename=bulk_models.BulkUpload)

urlpatterns = router.urls

urlpatterns += [
    path('template/', views.DownloadTemplateView.as_view(),
         name='download-template'),
    path('uploads/<idencode:pk>/:initiate',
         views.InitiateBulkUpload.as_view()),
    path('template/<idencode:pk>/', views.TemplateFieldsViewset.as_view()),
    path('template-check/', views.TemplateCheckView.as_view()),
    path('custom-template/', views.CustomTemplateView.as_view()),
    path('templates/', views.TemplateListView.as_view())
]
