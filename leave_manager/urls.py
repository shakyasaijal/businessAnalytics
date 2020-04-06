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
    path('', views.lms_index, name="lms_index"),
    path('apply-leave', views.apply_leave, name="lms_apply_leave"),
    path('leave-requests', views.get_leave_requests, name="get_leave_requests"),
    path('accept-leave', views.approve_leave, name="approve_leave"),
    path('reject-leave', views.reject_leave, name="reject_leave"),
]
