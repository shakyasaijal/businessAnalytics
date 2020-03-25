from django.shortcuts import render, redirect
from django.contrib import messages
from pprint import pprint
from django.urls import reverse
from django.http import HttpResponseRedirect
from services import models as services_model


def index(request):
    all_services = services_model.service_requested.objects.first()

    if all_services:
        for data in all_services.services.all():
            if data.service_name == "Website" and data.status:
                return render(request, "sysManager/index.html")
            else:
                return HttpResponseRedirect(reverse('crm_index'))
