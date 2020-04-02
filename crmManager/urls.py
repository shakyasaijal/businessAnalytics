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

# /crm
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.crm_index, name="crm_index"),
    path('<slug:slug>/', views.crm_branch, name="crm_branch"),
    path('weather/', views.weather, name="weather"),
    path('help-and-support/', views.help_support, name="help_support"),


    path('get-notification', views.get_notification, name="get_notification")
]