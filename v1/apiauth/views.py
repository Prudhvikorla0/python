
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView as SJWTTokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render

from base import exceptions
from base import session

from . import serializers as auth_serializers


# Create your views here.

class LoginView(TokenObtainPairView):
    """
    API to login User

    Takes in Tenant ID along with Email and password to login user with
    a session associated with the tenant/subdomain
    """
    serializer_class = auth_serializers.APILoginSerializer


class TokenRefreshView(SJWTTokenRefreshView):
    """
    API to Refresh Token

    Takes in the refresh token to provide a new Refresh and Access.
    Refresh token is refreshed to ensure that the user is only logged
    out if inactive for a long time
    """
    serializer_class = auth_serializers.TokenRefreshSerializer


class ResetPasswordView(generics.CreateAPIView):
    """
    API to reset user password

    Open API to reset user's password. An email will be sent to the email ID
    to verify and reset the password
    """
    permission_classes = ()
    authentication_classes = ()

    serializer_class = auth_serializers.APIPasswordResetSerializer


class ValidationView(generics.CreateAPIView):
    """
    API to verify Validate Email, password or Token

    This API can be used to validate any of Email-ID, Password or Validation token.

    Email and password fields are optional and can be sent alone.

    For validating Validation token, user id received in the url should also be supplied.
    """
    permission_classes = ()
    authentication_classes = ()

    serializer_class = auth_serializers.ValidationSerializer


class PasswordResetConfirmView(generics.CreateAPIView):
    """
    API to set user password

    Takes in the validation token and other information to change the user's
    password after validating the validation token
    """
    permission_classes = ()
    authentication_classes = ()

    serializer_class = auth_serializers.PasswordResetConfirmSerializer


class CheckPasswordView(generics.CreateAPIView):
    """
    Api to check user password.

    By taking the password as a parameter checks the password is belong the
    logged-in user.
    """

    serializer_class = auth_serializers.CheckPasswordSerializer


class UserTenantListView(generics.CreateAPIView):
    """
    Api to return list of tenants the user have access to
    """
    permission_classes = ()
    authentication_classes = ()

    serializer_class = auth_serializers.UserTenantSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        '''
        Setting up tenant data
        '''
        user = get_user_model().objects.get(username=request.data.get('email'))
        tenants = []
        for node_member in user.member_nodes.all():
            datum = {
                'id': node_member.tenant.idencode,
                'name': node_member.tenant.name
            }
            if datum not in tenants:
                tenants.append(datum)
        
        data = {
            'user': {
                'name': user.name,
            },
            'tenants': tenants,
        }

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


