"""URLs of the app accounts."""

from rest_framework import routers

from v1.products.views import product as product_viewset
from v1.products import models as product_models
from v1.products.views import batch as batch_viewset


router = routers.SimpleRouter()

router.register(r'batch', batch_viewset.BatchViewSet, 
    basename=product_models.Batch)
router.register(r'unit', product_viewset.UnitViewSet, 
    basename=product_models.Unit)
router.register(r'', product_viewset.ProductViewSet, 
    basename=product_models.Product)

urlpatterns = router.urls
