from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect


@login_required
def crm_index(request):
    return render(request, "crmManager/index.html")


