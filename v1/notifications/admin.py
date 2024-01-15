from django.contrib import admin

from common.admin import BaseAdmin
from common.admin import ReadOnlyAdmin

# Register your models here.

from . import models


@admin.register(models.Notification)
class NotificationAdmin(ReadOnlyAdmin):
    pass

@admin.register(models.SMSAlerts)
class SMSAlertsAdmin(ReadOnlyAdmin):
    list_display = ('phone', 'message')
