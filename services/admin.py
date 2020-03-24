from django.contrib import admin
from django.contrib.admin import AdminSite
from . import models 


class SuperAdmin(AdminSite):
    site_header = "Saijal Shakya"
    site_title = "Super Admin"
    index_title = "Super Admin - Saijal Shakya"

super_admin_site = SuperAdmin(name='super_admin')

super_admin_site.register(models.AllServices)
super_admin_site.register(models.service_requested)
