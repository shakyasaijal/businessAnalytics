from django.db import models
from django.utils import timezone
from datetime import datetime ,timedelta
from employee import models as employee_models
from leave_manager import models as leave_models
from support import models as support_models


class Notifications(models.Model):
    employee = models.ForeignKey(employee_models.Employee, on_delete=models.CASCADE,blank=True, null=True)

    leave = models.ForeignKey(leave_models.Leave, on_delete=models.CASCADE, blank=True, null=True)
    compensation = models.ForeignKey(leave_models.CompensationLeave, on_delete=models.CASCADE, blank=True, null=True)


    text = models.CharField(max_length=255, blank=True, null =True)

    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=datetime.now().time())
    expires_in = models.DateField(default=datetime.now()+timedelta(7))

    is_read = models.BooleanField(default=False, null=False, blank=False)
    tag = models.TextField(default='leave', null=False, blank=False)


    holiday = models.ForeignKey(leave_models.Holiday, on_delete=models.CASCADE, blank=True, null=True)
    # only for common notifications like notice, holiday
    seen_by = models.ManyToManyField(employee_models.Employee, blank=True, related_name="notification_seen_by")
    for_branch = models.ManyToManyField(support_models.Branches, blank=True, related_name="branch_notification")
    url = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name = verbose_name_plural = "Notification"
    
    def __str__(self):
        return "Notification{}".format(self.id)


    def notification_type(self):
        if self.leave:
            return "Leave"
        elif self.compensation:
            return "Compensation"
        elif self.holiday:
            return "Holiday"

    def notification_for(self):
        if self.employee:
            return self.employee.user.get_full_name()
        else:
            return '---'


class NotificationSettings(models.Model):
    employee = models.OneToOneField(employee_models.Employee, on_delete=models.CASCADE, null=False, blank=False)
    show_notification_icon = models.BooleanField(null=False, blank=False, default=True) # True will show count of notification in panel

    def __str__(self):
        return self.employee.user.get_full_name()

    class Meta:
        verbose_name = verbose_name_plural = "Notification Settings Per Employee"

    def employee_name(self):
        return self.employee.user.get_full_name()


        
