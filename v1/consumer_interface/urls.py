"""Urls under dashboard."""

from rest_framework import routers

from django.urls import path

from v1.consumer_interface import views as ci_view


urlpatterns = [

    path('tenant/<idencode:pk>/sections/', 
        ci_view.CISectionsView.as_view(), name='ci-section-data'),
    path('tenant/<idencode:pk>/theme/', 
         ci_view.CIThemeView.as_view(), name='ci-theme-data'),
    path('batch/<idencode:pk>/info/', ci_view.BatchInfoView.as_view()),
    path('batch/<idencode:pk>/chain/info/', 
         ci_view.BatchChainInfoView.as_view()),
]
