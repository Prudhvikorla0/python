from django.contrib import admin

from common.admin import BaseAdmin
from . import models
# Register your models here.


class RiskScoreAdmin(BaseAdmin):
    list_display = ('node', 'year', 'environment', 'social', 'governance', 'overall')


class CategoryScoreAdmin(BaseAdmin):
    list_display = ('score', 'average', 'risk_level', 'category')
    list_filter = ('risk_level', 'category')


class RiskCommentAdmin(BaseAdmin):
    list_display = ('score', 'severity')
    list_filter = ('severity',)


admin.site.register(models.RiskScore, RiskScoreAdmin)
admin.site.register(models.CategoryScore, CategoryScoreAdmin)
admin.site.register(models.RiskComment, RiskCommentAdmin)
