"""rightorigins_v3 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, register_converter

from base import views as base_views
from base import converters


register_converter(converters.IDConverter, 'idencode')

schema_view = get_schema_view(
   openapi.Info(
      title="RightOrigins V3 API",
      default_version='v1',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
   path('v1/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('admin/', admin.site.urls),
   path('v1/constants/', base_views.Constants.as_view(), name='constants'),
   path('v1/auth/', include('v1.apiauth.urls')),
   path('v1/accounts/', include('v1.accounts.urls')),
   path('v1/notifications/', include('v1.notifications.urls')),
   path('v1/supply-chain/', include('v1.supply_chains.urls')),
   path('v1/nodes/', include('v1.nodes.urls')),
   path('v1/tenants/', include('v1.tenants.urls')), 
   path('v1/dynamic-form/', include('v1.dynamic_forms.urls')),
   path('v1/products/', include('v1.products.urls')), 
   path('v1/transactions/', include('v1.transactions.urls')),
   path('v1/claims/', include('v1.claims.urls')),
   path('v1/bulk/', include('v1.bulk_templates.urls')),
   path('v1/dashboard/', include('v1.dashboard.urls')),
   path('v1/blockchain/', include('v1.blockchain.urls')),
   path('v1/tracker/', include('v1.tracker.urls')),
   path('v1/risk/', include('v1.risk.urls')),
   path('v1/ci/', include('v1.consumer_interface.urls')),
   path('v1/version-info/', base_views.Version.as_view(), name='version'),
   path('v1/questionnaire/', include('v1.questionnaire.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
