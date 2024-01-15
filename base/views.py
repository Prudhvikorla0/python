"""
Customizations for API views
"""
import re
from collections import defaultdict as dd

from django.db import models
from rest_framework import viewsets
from rest_framework.views import APIView

from base.response import SuccessResponse
from utilities.functions import decode


class IDEncodeLookupMixin:
    """
    Use this mixin for Viewsets to use encoded ID in url
    """
    def get_object(self):
        if 'id' in self.kwargs and not str(self.kwargs['id'].isdigit()):
            self.kwargs['id'] = decode(self.kwargs['id'])
        return super(IDEncodeLookupMixin, self).get_object()


class IdDecodeModelViewSet(viewsets.ModelViewSet):
    """
    Viewset to decode idencode to normal id
    """

    lookup_url_kwarg = 'idencode'

    def get_object(self):
        return self.basename.objects.get_by_encoded_id(self.kwargs['idencode'])


class Constants(APIView):
    """
    API to return configurations

    API lists al the configurations constants defined across the apps.
    """
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """
        Returns the list of constants used across the apps,
        categorized by app name.
        """
        constant_config = dd(lambda: dd(list))
        for defined_choices in models.IntegerChoices.__subclasses__():
            app_name = defined_choices.__module__.split('.')[1]
            choice_name = re.sub(r'(?<!^)(?=[A-Z])', '_', defined_choices.__name__).lower()
            constant_config[app_name][choice_name] = [
                {
                    'name': choice[1],
                    'id': choice[0]
                }for choice in defined_choices.choices
            ]
        return SuccessResponse(constant_config)


class Version(APIView):
    """
    View returns latest version detials.
    """
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """
        Get latest version from the settings and returns the info.
        """
        from versions.version_list import versions_info
        from django.conf import settings
        
        return SuccessResponse(versions_info[settings.VERSION])
