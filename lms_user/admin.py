from django.contrib import admin
from . import models
from services import models as services_model
from leave_manager import models as leave_models


class LmsAdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'leave_issuer_name')

admin.site.register(models.LmsUser, LmsAdmin)