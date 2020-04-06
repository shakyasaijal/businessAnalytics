from django.contrib import admin
from . import models


class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_name', 'contact', )
    search_fields = ['supplier_name', 'contact', ]

admin.site.register(models.Suppliers, SupplierAdmin)

class InventoryUserAdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'user_type')
    search_fields = ['employee_name', 'user_type']
    list_filter = ("user_type",)

admin.site.register(models.InventoryUser, InventoryUserAdmin)

class ProductsAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'cost_price', 'selling_price',)
    search_fields = ['name', 'quantity', 'cost_price', 'selling_price',]
    list_filter = ("branch", "supplier",)

admin.site.register(models.Product, ProductsAdmin)
