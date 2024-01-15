"""URLs of the app tenants."""

from rest_framework import routers
from django.urls import path

from v1.tenants.views import country as country_views
from v1.tenants.views import tenant as tenant_views
from v1.tenants.views import currency as currency_views
from v1.tenants.views import category as category_views
from v1.tenants import models as tenant_models

router = routers.SimpleRouter()

router.register(r'countries', country_views.CountryViewSet,
    basename=tenant_models.Country)
router.register(r'provinces', country_views.ProvinceViewSet,
    basename=tenant_models.Province)
router.register(r'region', country_views.RegionViewSet,
    basename=tenant_models.Region)
router.register(r'villages', country_views.VillageViewSet,
    basename=tenant_models.Village)
router.register(r'currencies', currency_views.CurrencyViewSet,
    basename=tenant_models.Currency)
router.register(r'categories', category_views.CategoryViewSet,
    basename=tenant_models.Category)
router.register(
    r'tags', tenant_views.TagViewSet,
    basename=tenant_models.Tag)
urlpatterns = router.urls

urlpatterns += [
    # Authentication APIS
    path('domain/validate/', tenant_views.ValidateTenantView.as_view(), 
    name='validate_tenant'), 
    path('', tenant_views.TenantDetailView.as_view(), 
    name='tenant_detail'), 
]
