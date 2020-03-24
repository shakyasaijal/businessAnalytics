from django.db import models
from django.contrib.auth.models import User
from helper import inventory as inventory_helper


class Branches(models.Model):
    branch_name = models.CharField(max_length=255, null=False, blank=False)
    location = models.TextField(null=False, blank=False)
    contact = models.CharField(max_length=255, null=False, blank=False)
    branch_head = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.branch_name

    class Meta:
        verbose_name = verbose_name_plural = "Branches"


class Suppliers(models.Model):
    supplier_name = models.CharField(max_length=255, null=False, blank=False)
    contact = models.TextField(null=True, blank=True)
    branch = models.ManyToManyField(Branches, blank=True, related_name = "branch_supplier")
    # product

    def __str__(self):
        return self.supplier_name

    class Meta:
        verbose_name = verbose_name_plural = "Suppliers"


class Product(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    quantity = models.CharField(max_length=255, null=True, blank=True)
    cost_price = models.CharField(max_length = 255, null=True, blank=True)
    selling_price = models.CharField(max_length = 255, null=True, blank=True)
    supplier = models.ManyToManyField(Suppliers, blank=True)
    branch = models.ManyToManyField(Branches, blank=False)


    class Meta:
        verbose_name = verbose_name_plural = "Products"

    def __str__(self):
        return self.name


class InventoryUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee')
    user_type = models.CharField(max_length = 50, null=False, blank=False, choices=inventory_helper.user_type)
    contact = models.CharField(max_length=255, null=True, blank=True)
    branch = models.ManyToManyField(Branches, blank=False)

    class Meta:
        verbose_name = verbose_name_plural = "Inventory User"

    def __str__(self):
        return self.user.get_full_name()

    