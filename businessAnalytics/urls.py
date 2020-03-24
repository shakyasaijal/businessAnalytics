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
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
