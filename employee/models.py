from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.core.files import File
from datetime import datetime
import os
from django.dispatch import receiver
from inventory import models as inventory_model
from support import models as support_models
from helper.common import common as helper
from multiselectfield import MultiSelectField


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
    department_head = models.ForeignKey(User, on_delete=models.CASCADE, related_name='department_head', null=False, blank=False)

    def __str__(self):
        return self.department_name
    
    class Meta:
        verbose_name = verbose_name_plural = "All Departments"


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    department = models.ManyToManyField(Department, verbose_name="Employee Departments", blank=False)
    date_of_birth = models.DateField(auto_now_add=False)
    joined_date = models.DateField(auto_now_add=False, null=True, blank=True)
    branch = models.ManyToManyField(support_models.Branches, blank=False)
    contact = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    pan_document = models.FileField(verbose_name="PAN Document",upload_to="employee/static/employee/pan/", null=True, blank=True)
    picture = models.ImageField(upload_to=employee_image, null=False, blank=False)
    user_type = MultiSelectField(choices=helper.employee_type)
    staff_head = models.ForeignKey('self', on_delete=models.PROTECT, related_name="employee_staff_head", null=True, blank=True, help_text="If Ownership, then not required.")
    fcm_token = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name()

    def get_associated_name(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = verbose_name_plural = "Employee Information"

    def image_tag(self):
        try:
            return mark_safe('<img src="%s" width="150" height="150" />' % (self.picture.url))
        except Exception as e:
            print(e)

    def file_tag(self):
        try:
            return mark_safe('<a href="%s">View File<a/>' % (self.pan_document.url))
        except Exception as e:
            print(e)

    image_tag.short_description = 'Image'
    file_tag.short_description = 'PAN DOC'

    def _branch_(self):
        return ", ".join([str(p) for p in self.branch.all()])


class Salary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="employee_salary")
    salary = models.IntegerField(null=False, blank=False)
    month = models.DateField(null=False, blank=False)

    def __str__(self):
        return self.employee.user.get_full_name()

    class Meta:
        verbose_name = verbose_name_plural = "Employees Salary"

    def employee_name(self):
        return self.employee.user.get_full_name()


@receiver(models.signals.post_delete, sender=Employee)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    try:
        if sender.__name__ == 'Employee':
            if instance.picture:
                if os.path.isfile(instance.picture.path):
                    os.remove(instance.picture.path)
    except Exception as e:
        print('Delete on change', e)
        pass


@receiver(models.signals.pre_save, sender=Employee)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    old_file = ""
    new_file = ""
    try:
        if sender.__name__ == "Employee":
            old_file = sender.objects.get(pk=instance.pk).picture
            new_file = instance.picture
    except sender.DoesNotExist:
        return False

    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

