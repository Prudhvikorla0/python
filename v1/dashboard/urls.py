"""Urls under dashboard."""

from rest_framework import routers

from django.urls import path

from v1.dashboard.views import theme as theme_views
from v1.dashboard.views import dashboard as dashboard_views
from v1.dashboard import models as dashboad_models


urlpatterns = [
    path('connection/stats/', dashboard_views.ConnectionStatsView.as_view(), 
    name='connection-statistics'), 
    path('tenant/<idencode:id>/theme/', theme_views.DashBoardThemeView.as_view(), 
    name='dashboard-theme-retrieve'), 
    path('tenant/<idencode:id>/tracker/theme/<slug:name>/', 
    theme_views.TrackerThemeView.as_view(), 
    name='tracker-theme-retrieve'), 
    path('supplier/stats/', dashboard_views.SupplierStatsView.as_view(),
    name='supplier-statistics'),
    path('product/<idencode:pk>/stats/', dashboard_views.ProductStatsView.as_view(),
    name='product-statistics'),
    path('esg/stats/', dashboard_views.ESGStatsView.as_view(),
    name='esg-statistics'),
    path('risk/stats/', dashboard_views.RiskStatsView.as_view(),
    name='risk-statistics'),

]
