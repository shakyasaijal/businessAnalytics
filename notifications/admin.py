from django.contrib import admin
from . import models


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'notification_for')

admin.site.register(models.Notifications, NotificationAdmin)


class NotifySettingAdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'show_notification_icon')

admin.site.register(models.NotificationSettings, NotifySettingAdmin)
