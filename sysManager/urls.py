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
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login_view, name="login_view"),
    path('login-controller', views.login_controller, name="login_controller"),
    path('crm/', include('crmManager.urls')),
]