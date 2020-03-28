'''
Author: Saijal Shakya
Development:
    > LMS: December 20, 2018
    > HRM: Febraury 15, 2019
    > CRM: March, 2020
    > Inventory Sys: April, 2020
    > Analytics: ...
License: Credited
Contact: https://saijalshakya.com.np
'''
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.hr_index, name="hr_index"),
    path('employees/', views.hr_employee, name="hr_employee"),
    path('employees/<int:id>', views.hr_employee_by_id, name="hr_employee_by_id")
]


