from django.contrib import admin
from . import models


class BranchAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('branch_name',)}
    list_display = ('branch_name','location', 'contact', 'branch_head')
    search_fields = ['branch_name', 'location', 'contact', 'branch_head']
    list_filter = ("location",)

admin.site.register(models.Branches, BranchAdmin)