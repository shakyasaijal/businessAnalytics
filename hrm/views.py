from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.models import Q
import datetime
from pprint import pprint
from services import models as service_models
from helper.common import manager as common_helper
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

import yaml
credential = yaml.load(open('credentials.yaml'), Loader=yaml.FullLoader)

template_version = ''
try:
    template_version = credential['template_version']
except Exception as e:
    template_version = 'v1'

@login_required
@cache_page(CACHE_TTL)
def hr_index(request):
    if common_helper.has_hrm_service():
        hr_service_expiry = common_helper.is_hrm_expired()
        if hr_service_expiry<0:
            messages.error(request, "Your HRM service has been expired. Please renew or activate the service. Thank You. <a href='/'>Get Help</a>")
            return HttpResponseRedirect(reverse('crm_index'))
        else:
            if common_helper.has_hrm_access_to_user(request):
                return render(request, "hrm/"+template_version+"/index.html")
            else:
                messages.error(request, "You dont have access to HRM. Please contact your HR Manager.")
                return HttpResponseRedirect(reverse('crm_index'))
    else:
        messages.error(request, "Sorry. You don't have HRM service activated.")
        return HttpResponseRedirect(reverse('crm_index'))


@login_required
@cache_page(CACHE_TTL)
def hr_employee(request):
    
    if common_helper.has_hrm_service():
        hr_service_expiry = common_helper.is_hrm_expired()
        if hr_service_expiry<0:
            messages.error(request, "Your HRM service has been expired. Please renew or activate the service. Thank You. <a href='/'>Get Help</a>")
            return HttpResponseRedirect(reverse('crm_index'))
        else:
            if common_helper.has_hrm_access_to_user(request):
                hr_user_type = common_helper.hr_user_type(request)
                
                branches = common_helper.get_current_user_branch(request.user)
                all_emp = common_helper.get_all_employee_by_branch(branches[0])     
                print(all_emp)
                return render(request, "hrm/"+template_version+"/employee_by_branch.html")
            else:
                messages.error(request, "You dont have access to HRM. Please contact your HR Manager.")
                return HttpResponseRedirect(reverse('crm_index'))
    else:
        messages.error(request, "Sorry. You don't have HRM service activated.")
        return HttpResponseRedirect(reverse('crm_index'))
