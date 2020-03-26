from django.contrib import admin
from . import models


admin.site.register(models.Department)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('get_associated_name', 'contact','image_tag', 'file_tag', '_branch_',)
    readonly_fields = ['image_tag', 'file_tag']
    search_fields = ['get_associated_name', 'contact', 'address', 'phone']
    list_filter = ("department",)

admin.site.register(models.Employee, EmployeeAdmin)
