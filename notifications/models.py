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
    holiday = models.ForeignKey(leave_models.Holiday, on_delete=models.CASCADE, blank=True, null=True)
    for_branch = models.ManyToManyField(support_models.Branches, blank=True, null=True, related_name="branch_notification")
    text = models.CharField(max_length=255, blank=True, null =True)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=datetime.now().time())
    expires_in = models.DateField(default=datetime.now()+timedelta(7))
    is_read = models.BooleanField(default=False, null=False, blank=False)
    tag = models.TextField(default='leave', null=False, blank=False)

    class Meta:
        verbose_name = verbose_name_plural = "Notification"
    
    def __str__(self):
        return "Notification{}".format(self.id)

