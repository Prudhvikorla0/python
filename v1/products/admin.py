"""Models are registered with django admin at here."""

from django.contrib import admin

from common.admin import BaseAdmin

from v1.products import models as product_models


class UnitAdmin(BaseAdmin):
    list_display = ('name', 'idencode', 'factor',)
    list_filter = ('is_active',)

    search_fields = ['name']


class ProductAdmin(BaseAdmin):
    list_display = ('name', 'idencode', 'supply_chain',)
    list_filter = ('supply_chain', 'is_active')
    readonly_fields = ('product_specific_form',)
    search_fields = ['name']


class BatchAdmin(BaseAdmin):
    list_display = ('product', 'name', 'node', 'idencode', 
        'initial_quantity', 'current_quantity')
    search_fields = ['name', 'number']
    
class ProductTypeAdmin(BaseAdmin):
    list_display = ('name', 'idencode', 'supply_chain',)
    list_filter = ('supply_chain', 'is_active')

    search_fields = ['name']


admin.site.register(product_models.Unit, UnitAdmin)
admin.site.register(product_models.Product, ProductAdmin)
admin.site.register(product_models.Batch, BatchAdmin)
admin.site.register(product_models.ProductType, ProductTypeAdmin)
