"""Models are registered with django admin at here."""

from django.contrib import admin

from v1.dashboard import models as dashboard_models

from common.admin import BaseAdmin


class DashboardAdmin(BaseAdmin):
    list_display = ('tenant', )


class TrackerThemeAdmin(BaseAdmin):
    list_display = ('tenant', )

admin.site.register(dashboard_models.DashboardTheme, DashboardAdmin)
admin.site.register(dashboard_models.TrackerTheme, TrackerThemeAdmin)
