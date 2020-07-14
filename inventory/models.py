from django.db import models
from django.contrib.auth.models import User
from helper import inventory as inventory_helper
from employee import models as employee_models
from support import models as support_models



class Suppliers(models.Model):
    supplier_name = models.CharField(max_length=255, null=False, blank=False)
    contact = models.TextField(null=True, blank=True)
    branch = models.ManyToManyField(support_models.Branches, blank=True, related_name = "branch_supplier")
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
    branch = models.ManyToManyField(support_models.Branches, blank=False)


    class Meta:
        verbose_name = verbose_name_plural = "Products"

    def __str__(self):
        return self.name


class InventoryUser(models.Model):
    users = models.ForeignKey(employee_models.Employee, on_delete=models.PROTECT, related_name='inventory_user')
    user_type = models.CharField(max_length = 50, null=False, blank=False, choices=inventory_helper.user_type)

    class Meta:
        verbose_name = verbose_name_plural = "Inventory User"

    def __str__(self):
        return self.users.user.get_full_name()

    def employee_name(self):
        return self.users.user.get_full_name()

    