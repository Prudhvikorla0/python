"""URLs of the app dynamic-forms."""

from rest_framework import routers
from django.urls import path

from v1.dynamic_forms import models as form_models
from v1.dynamic_forms.views import form as form_viewset

router = routers.SimpleRouter()

# apis to list fields under a form.
router.register(r'', form_viewset.FormViewSet, 
    basename=form_models.Form)

# apis to list , create and update form field values.
urlpatterns = [
    path('submission/', form_viewset.FormSubmissionCreateView.as_view(), 
    name='create-submission-form'),
    path('submission/<idencode:pk>/', 
    form_viewset.FormSubmissionView.as_view(), name='submit-form'), 
    path('field/<idencode:pk>/', form_viewset.FieldValueUpdateView.as_view(), 
    name='update-field-value')
]

urlpatterns += router.urls
