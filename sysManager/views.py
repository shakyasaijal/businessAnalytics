from django.shortcuts import render, redirect
from django.contrib import messages
from pprint import pprint
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from services import models as services_model
from helper.common import common as web_common


def index(request):
    all_services = services_model.service_requested.objects.first()

    if all_services:
        for data in all_services.services.all():
            if data.service_name == "Website" and data.status:
                return render(request, "sysManager/index.html")
            else:
                return HttpResponseRedirect(reverse('crm_index'))


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    return render(request, "sysManager/login.html")


def login_controller(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    if not request.method == "POST":
        messages.warning(request, "Something went wrong.")
        return HttpResponseRedirect(reverse('login_view'))

    errors = web_common.login_field_error_validate(request)
    if not errors:
        user = authenticate(
            request, username=request.POST["username"], password=request.POST["password"])
        if user:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(
                request, "You are successfully signed in.", extra_tags="1")
            return HttpResponseRedirect(reverse('index'))
        else:
            messages.error(request, "Invalid Credentials.")
            return render(request, "sysManager/login.html")
    else:
        messages.error(request, errors[0], extra_tags="0")
        return render(request, "sysManager/login.html")
