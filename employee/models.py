from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.core.files import File
from datetime import datetime
import os
from django.dispatch import receiver


def employee_image(instance, filename):
    upload_to = 'employee/static/employee/images/'
    ext = filename.split('.')[-1]
    # get filename
    file_extension = filename.split('.')[1]
    _datetime = datetime.now()
    datetime_str = _datetime.strftime("%Y-%m-%d-%H-%M-%S")
    date_format = datetime_str.split('-')
    date_join = ''.join(date_format)

    filename = '{}.{}'.format(date_join, ext)
    return os.path.join(upload_to, filename)


class Department(models.Model):
    department_name = models.CharField(max_length=255, null=False, blank=False, unique=True, help_text="LMS, HRM, CRM, Inventory Management")
    department_head = models.ForeignKey(User, on_delete=models.CASCADE, related_name='department_head', null=True, blank=True)

    def __str__(self):
        return self.department_name
    
    class Meta:
        verbose_name = verbose_name_plural = "All Departments"


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    contact = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    pan_document = models.FileField(verbose_name="PAN Document",upload_to="employee/static/employee/pan/", null=True, blank=True)
    picture = models.ImageField(upload_to=employee_image, null=True, blank=True)
    department = models.ManyToManyField(Department, verbose_name="Employee Departments", blank=False)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = verbose_name_plural = "Employee Information"
