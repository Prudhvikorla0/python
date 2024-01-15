from rest_framework import authentication

from django.utils.translation import gettext_lazy as _

from base import exceptions
from utilities.functions import decode

from v1.accounts.models import ValidationToken

class ValidationTokenAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class to authenticate using validation token.
    """
    def authenticate(self, request):
        token = request.query_params.get('token',None)
        salt = request.query_params.get('salt',None)
        if token and salt:
            try:
                validation_token = ValidationToken.objects.get(
                    key=token,id=decode(salt))
                request.token = validation_token
            except:
                raise exceptions.AuthenticationFailed(
                    _("Token does not exist."))
            if validation_token.is_valid():
                return None
        raise exceptions.AuthenticationFailed(_("Token authentication failed."))
