from django.db import models
from helper import singletonModel
from django.utils.safestring import mark_safe
from django.core.files import File
from datetime import datetime
import os
from django.dispatch import receiver


def services_image(instance, filename):
    upload_to = 'services/static/services/images/'
    ext = filename.split('.')[-1]
    # get filename
    file_extension = filename.split('.')[1]
    _datetime = datetime.now()
    datetime_str = _datetime.strftime("%Y-%m-%d-%H-%M-%S")
    date_format = datetime_str.split('-')
    date_join = ''.join(date_format)

    filename = '{}.{}'.format(date_join, ext)
    return os.path.join(upload_to, filename)


class AllServices(models.Model):
    service_name = models.CharField(max_length=255, null=False, blank=False)
    picture = models.ImageField(upload_to=services_image, null=False, blank=False)

    def __str__(self):
        return self.service_name

    class Meta:
        verbose_name = verbose_name_plural = "All Services"


class service_requested(singletonModel.SingletonModel):
    company_name = models.CharField(max_length=255, null=False, blank=False)
    owner_name = models.CharField(max_length=255, null=False, blank=False)
    project_started = models.DateField(auto_now_add=True)
    domain = models.URLField(null=False, blank=False)
    api = models.URLField(null=True, blank=True)
    services = models.ManyToManyField(AllServices, blank=False)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = verbose_name_plural = "Service Requested"


@receiver(models.signals.post_delete, sender=AllServices)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    try:
        if sender.__name__ == 'AllServices':
            if instance.picture:
                if os.path.isfile(instance.picture.path):
                    os.remove(instance.picture.path)
    except Exception as e:
        print('Delete on change', e)
        pass


@receiver(models.signals.pre_save, sender=AllServices)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    old_file = ""
    new_file = ""
    try:
        if sender.__name__ == "AllServices":
            old_file = sender.objects.get(pk=instance.pk).picture
            new_file = instance.picture
    except sender.DoesNotExist:
        return False

    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

