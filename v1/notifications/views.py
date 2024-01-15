"""
APIs for Notifications
"""
from drf_yasg.utils import swagger_auto_schema

from django.shortcuts import render
from django.db.models import Count
from django.conf import settings
from rest_framework import generics
from rest_framework import views
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from base import session
from base import exceptions
from utilities.functions import encode

from v1.notifications.models import Notification
from v1.notifications import filters as noti_filters
from v1.notifications import serializers

# Create your views here.


class NotificationSummaryView(views.APIView):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        notif_summary = Notification.objects.filter(
            user_id=session.get_from_local('user_id'),
            tenant_id__in=[session.get_from_local('tenant_id'), None],
            visibility=True
        ).exclude(target_node=None).values(
            'target_node', 'target_node__name', 'target_node__image'
        ).annotate(
            count=Count('id'), 
            unread_count=Count('id', filter=Q(is_read=False))
        ).order_by('-count')

        notification_data = []
        for notif in notif_summary:
            notification_data.append(
                {
                    'count': notif['count'],
                    'unread_count': notif['unread_count'],
                    'node': {
                        'id': encode(notif['target_node']) if notif['target_node'] else None,
                        'name': notif['target_node__name'],
                        'image': f"https:{settings.MEDIA_URL}{notif['target_node__image']}" \
                            if notif['target_node__image'] else ""
                    }
                }
            )
        return Response(notification_data)


class NotificationsListView(generics.ListAPIView):
    """
    API to list notifications with option to filter by node
    """

    serializer_class = serializers.NotificationSerializer
    filterset_class = noti_filters.NotificationFilter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'body']

    def get_queryset(self):
        return Notification.objects.filter(
            user_id=session.get_from_local('user_id'),
            tenant_id__in=[session.get_from_local('tenant_id'), None],
            visibility=True).exclude(target_node=None).select_related(
            'actor_node', 'target_node', 'supply_chain', 'creator')


class NotificationReadView(views.APIView):
    """
    API to mark notifications as read.
    """
    http_method_names = ['patch']

    @swagger_auto_schema(request_body=serializers.ReadNotificationSerializer)
    def patch(self, request, *args, **kwargs):
        notification_serializer = serializers.ReadNotificationSerializer(
            data=request.data)
        if notification_serializer.is_valid():
            notification_serializer.save()
            return Response(notification_serializer.data)
        raise exceptions.BadRequest(notification_serializer.errors)
