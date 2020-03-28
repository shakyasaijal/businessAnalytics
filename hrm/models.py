from django.db import models
from employee import models as employee_models
from helper import hrm as hrm_helper
from support import models as support_models


class hr_user(models.Model):
    employee = models.ForeignKey(employee_models.Employee, related_name="hr_employee", on_delete=models.PROTECT)
    hr_type = models.CharField(max_length = 255, null=False, blank=False, choices=hrm_helper.hr_type)
    branch = models.ManyToManyField(support_models.Branches, related_name="hr_branch", blank=True)

    def __str__(self):
        return self.employee.user.get_full_name()

    class Meta:
        verbose_name = verbose_name_plural = "HRM Users"

    def employee_name(self):
        return self.employee.user.get_full_name()

    def _branch_(self):
        if self.branch.all():
            return ", ".join([str(p) for p in self.branch.all()])
        else:
            return "All Branch"


class Payroll(models.Model):
    employee = models.ForeignKey(employee_models.Employee, related_name="payroll_employee", on_delete=models.PROTECT)
    month = models.DateField(null=False, blank=False)
    is_paid = models.BooleanField(null=False, blank=False, default=False) #False = not paid, True = paid

    def __str__(self):
        return self.employee.user.get_full_name()

    class Meta:
        verbose_name = verbose_name_plural = "Employee Payroll"

    def employee_name(self):
        return self.employee.user.get_full_name()
        