"""Models are registered with django admin at here."""

from django.contrib import admin

from v1.consumer_interface import models as ci_models

from common.admin import BaseAdmin


class SectionAdmin(BaseAdmin):
    """ Admin for Purchase order """
    list_display = ('idencode', 'id', 'name', 'key')
    search_fields = ['name', 'key','id']
    list_filter = ('is_default', 'sections__tenant')

class SectionTenantRegisterAdmin(BaseAdmin):
    """ Admin for Purchase order """
    list_display = ('idencode', 'tenant', 'section')
    search_fields = ['tenant__name', 'section_object_id']
    list_filter = ('tenant',)

admin.site.register(ci_models.Header,SectionAdmin)
admin.site.register(ci_models.OverViewSection,SectionAdmin)
admin.site.register(ci_models.InfoSection,SectionAdmin)
admin.site.register(ci_models.MapSection,SectionAdmin)
admin.site.register(ci_models.SupplyChainSection,SectionAdmin)
admin.site.register(ci_models.AboutSection,SectionAdmin)
admin.site.register(ci_models.MoreInfoSection,SectionAdmin)
admin.site.register(
    ci_models.SectionTenantRegister, SectionTenantRegisterAdmin)
admin.site.register(ci_models.Footer,SectionAdmin)
admin.site.register(ci_models.CICard,BaseAdmin)
admin.site.register(ci_models.CITheme,BaseAdmin)
