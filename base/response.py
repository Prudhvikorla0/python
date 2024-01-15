"""Custom render class to custom success response."""

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status as rest_statuses


class ApiRenderer(JSONRenderer):
    """Custom render class."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Custom render function."""
        response_data = data
        try:
            if not data['success']:
                response_data = data
        except:
            response_data = {
                'success': True,
                'detail': 'Success',
                'code': renderer_context['response'].status_code,
                'data': data
            }

        response = super(ApiRenderer, self).render(
            response_data, accepted_media_type, renderer_context)

        return response


class SuccessResponse(Response):
    """
    Over-ridden to change code structure and update status codes
    """

    def __init__(
            self, response=None, message=None, status=rest_statuses.HTTP_200_OK,
            default_data={},*args, **kwargs):
        data = response if response else default_data
        response = {
            'success': True,
            'detail': message,
            'code': status,
            'data': data
        }
        if not message:
            response['detail'] = 'Success.'
        super(SuccessResponse, self).__init__(response, status, *args, **kwargs)
