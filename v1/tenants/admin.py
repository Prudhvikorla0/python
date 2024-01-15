"""Models are registered with django admin at here."""

from django.contrib import admin
from django.http import HttpResponseRedirect
from inflection import underscore

from common.admin import BaseAdmin

from v1.tenants import models as tenant_models

from admin_extra_buttons.api import ExtraButtonsMixin, view, choice


class TenantAdmin(ExtraButtonsMixin, BaseAdmin):

    def get_queryset(self, request):
        """overrided to remove n+1 query issue."""
        return super().get_queryset(request).prefetch_related(
            'countries', 'currencies').select_related(
            'node_form', 'node_member_form', 'internal_transaction_form',
            'external_transaction_form', 'claim_form', 'txn_enquiry_form', 'env_data_form', 
            'soc_data_form', 'gov_data_form').all()

    list_display = ('name', 'idencode',)
    search_fields = ['name']
    search_help_text = "NOTE : Here you can add Node Member and Node Supply Chain from \
        the Node dropdown. Likewise all the respective links are given below under \
        their respective dropdowns"

    @choice(change_list=True)
    def Tenant(self, button):
        button.choices = [self.add_operations, self.add_country, 
            self.add_currency, self.add_supply_chain, self.add_products, 
            self.add_unit]
    
    @choice(change_list=True)
    def Node(self, button):
        button.choices = [self.add_node, self.add_node_member, 
            self.add_node_supply_chain]
    
    @choice(change_list=True)
    def Claim(self, button):
        button.choices = [self.add_claims, self.add_criterion]
    
    @choice(change_list=True)
    def Template(self, button):
        button.choices = [self.add_template]
    
    @choice(change_list=True)
    def Dynamic_Forms(self, button):
        button.choices = [self.add_forms, self.add_form_field]

    @view()
    def add_operations(self, request):
        return HttpResponseRedirect(
            "http://0.0.0.0:8000/admin/supply_chains/operation/add/")
    
    @view()
    def add_country(self, request):
        return HttpResponseRedirect(
            "http://0.0.0.0:8000/admin/tenants/country/add/")
    
    @view()
    def add_currency(self, request):
        return HttpResponseRedirect(
            "http://0.0.0.0:8000/admin/tenants/currency/add/")
    
    @view()
    def add_supply_chain(self, request):
        return HttpResponseRedirect(
            "http://0.0.0.0:8000/admin/supply_chains/supplychain/add/")
    
    @view()
    def add_products(self, request):
        return HttpResponseRedirect(
            "http://0.0.0.0:8000/admin/products/product/add/")

    @view()
    def add_node(self, request):
        return HttpResponseRedirect(
            "http://0.0.0.0:8000/admin/nodes/node/add/")
    
    @view()
    def add_node_member(self, request):
        return HttpResponseRedirect(
            "http://0.0.0.0:8000/admin/nodes/nodemember/add/")
    
    @view()
    def add_node_supply_chain(self, request):
        return HttpResponseRedirect(
            "http://0.0.0.0:8000/admin/supply_chains/nodesupplychain/add/")
    
    @view()
    def add_template(self, request):
        return HttpResponseRedirect(
            "http://0.0.0.0:8000/admin/bulk_templates/template/add/")
    
    @view()
    def add_claims(self, request):
        return HttpResponseRedirect(
            "http://0.0.0.0:8000/admin/claims/claim/add/")

    @view()
    def add_criterion(self, request):
        return HttpResponseRedirect(
            "http://0.0.0.0:8000/admin/claims/criterion/add/")
    
    @view()
    def add_forms(self, request):
        return HttpResponseRedirect(
            "http://0.0.0.0:8000/admin/dynamic_forms/form/add/")
    
    @view()
    def add_form_field(self, request):
        return HttpResponseRedirect(
            "http://0.0.0.0:8000/admin/dynamic_forms/formfield/add/")
    
    @view()
    def add_unit(self, request):
        return HttpResponseRedirect(
            "http://0.0.0.0:8000/admin/products/unit/add/")
    

class TenantAdminAdmin(BaseAdmin):
    list_display = ('tenant', 'user', 'idencode',)
    list_filter = ('type', )
    search_fields = ['user__name']


class CountryAdmin(BaseAdmin):
    list_display = (
        'name', 'alpha_2', 'dial_code', 'latitude','longitude', 'idencode',)
    search_fields = ['name', 'code', 'dial_code',]


class ProvinceAdmin(BaseAdmin):
    list_display = (
        'country', 'name', 'latitude','longitude', 'idencode',)
    search_fields = ['name']


class RegionAdmin(BaseAdmin):
    list_display = (
        'province', 'name', 'idencode',)
    search_fields = ['name']


class VillageAdmin(BaseAdmin):
    list_display = (
        'region', 'name', 'idencode',)
    search_fields = ['name']


class CurrencyAdmin(BaseAdmin):
    list_display = (
        'name', 'code', 'idencode',)
    search_fields = ['name']


class CategoryAdmin(BaseAdmin):
    list_display = (
        'name', 'tenant', 'idencode',)
    search_fields = ['name']
    list_filter = ('type', 'tenant')


class TagAdmin(BaseAdmin):
    list_display = ('name', 'idencode',)
    search_fields = ['name']


admin.site.register(tenant_models.Tenant, TenantAdmin)
admin.site.register(tenant_models.TenantAdmin, TenantAdminAdmin)
admin.site.register(tenant_models.Country, CountryAdmin)
admin.site.register(tenant_models.Province, ProvinceAdmin)
admin.site.register(tenant_models.Currency, CurrencyAdmin)
admin.site.register(tenant_models.Category, CategoryAdmin)
admin.site.register(tenant_models.Region, RegionAdmin)
admin.site.register(tenant_models.Village, VillageAdmin)
admin.site.register(tenant_models.Tag, TagAdmin)
