from django.contrib import admin
from . import models 

class HRUserdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'hr_type', '_branch_')
    search_fields = ('employee_name', 'hr_type')
    list_filter = ('hr_type',)

admin.site.register(models.hr_user, HRUserdmin)

class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'month', 'is_paid')
    search_fields = ('employee_name', 'month', 'is_paid')

admin.site.register(models.Payroll, PayrollAdmin)