from django.db import models
from employee import models as employee_models


class LmsUser(models.Model):
    employee = models.OneToOneField(employee_models.Employee, on_delete=models.CASCADE, related_name = "lms_employee")
    leave_issuer = models.ForeignKey(employee_models.Employee, on_delete=models.CASCADE, related_name="lms_issuer", null=True, blank=True, help_text="If blanked, staff head will be leave issuer.")

    def __str__(self):
        return self.employee.user.get_full_name()

    class Meta:
        verbose_name = verbose_name_plural = "Access to Leave Management System"

    def employee_name(self):
        return self.employee.user.get_full_name()

    def leave_issuer_name(self):
        leave_issuer = ''
        if self.leave_issuer:
            leave_issuer = self.leave_issuer.user.get_full_name()
        else:
            leave_issuer = self.employee.staff_head.get_full_name()
        return leave_issuer
        