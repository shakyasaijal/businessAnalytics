from django.db import models


class Branches(models.Model):
    branch_name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    slug = models.SlugField(null=False, blank=False, unique=False, help_text = "IGNORE THIS FIELD.")
    location = models.TextField(null=False, blank=False)
    contact = models.CharField(max_length=255, null=False, blank=False)
    branch_head = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.branch_name

    class Meta:
        verbose_name = verbose_name_plural = "Branches"
