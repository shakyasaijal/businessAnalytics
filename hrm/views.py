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
from django.core.cache import cache
from helper.common import redis

from employee import models as employee_models
from support import models as support_models
from helper.common import common as common


CACHE_TTL = getattr(settings, 'CACHE_TTL', settings.CACHE_TTL)

import yaml
credential = yaml.load(open('credentials.yaml'), Loader=yaml.FullLoader)

template_version = ''
try:
    template_version = credential['template_version']
except Exception as e:
    template_version = 'v1'

@login_required
def hr_index(request):
    if common_helper.has_hrm_service():
        hr_service_expiry = common_helper.is_hrm_expired()
        if hr_service_expiry<0:
            messages.error(request, "Your HRM service has been expired. Please renew or activate the service. Thank You. <a href='/'>Get Help</a>")
            return HttpResponseRedirect(reverse('crm_index'))
        else:
            if common_helper.has_hrm_access_to_user(request.user)[1]:
                if 'crm_branch' not in cache:
                    redis.set_crm_branch(request)

                current_branch = cache.get('crm_branch')
                return render(request, "hrm/"+template_version+"/index.html", context = {"current_branch": current_branch})
            else:
                messages.error(request, "You dont have access to HRM. Please contact your HR Manager.")
                return HttpResponseRedirect(reverse('crm_index'))
    else:
        messages.error(request, "Sorry. You don't have HRM service activated.")
        return HttpResponseRedirect(reverse('crm_index'))


@login_required
def hr_employee(request):
    if common_helper.has_hrm_service():
        hr_service_expiry = common_helper.is_hrm_expired()
        if hr_service_expiry<0:
            messages.error(request, "Your HRM service has been expired. Please renew or activate the service. Thank You. <a href='/'>Get Help</a>")
            return HttpResponseRedirect(reverse('crm_index'))
        else:
            if common_helper.has_hrm_access_to_user(request.user)[1]:
                
                context = {}
                if 'crm_branch' not in cache:
                    redis.set_crm_branch(request)

                current_branch = cache.get('crm_branch')
                context.update({
                    "current_branch": current_branch
                })

                all_emp = common_helper.get_all_employee_by_branch(current_branch)     
                context.update({"all_emp": all_emp})

                return render(request, "hrm/"+template_version+"/employee_by_branch.html", context=context)
            else:
                messages.error(request, "You dont have access to HRM. Please contact your HR Manager.")
                return HttpResponseRedirect(reverse('crm_index'))
    else:
        messages.error(request, "Sorry. You don't have HRM service activated.")
        return HttpResponseRedirect(reverse('crm_index'))


@login_required
def hr_employee_by_id(request, id):
    if common_helper.has_hrm_service():
        hr_service_expiry = common_helper.is_hrm_expired()
        if hr_service_expiry<0:
            messages.error(request, "Your HRM service has been expired. Please renew or activate the service. Thank You. <a href='/'>Get Help</a>")
            return HttpResponseRedirect(reverse('crm_index'))
        else:
            hrm_access = common_helper.has_hrm_access_to_user(request.user)
            if hrm_access[1]:
                context = {}
                if 'crm_branch' not in cache:
                    redis.set_crm_branch(request)

                current_branch = cache.get('crm_branch')
                context.update({
                    "current_branch": current_branch
                })

                all_emp = common_helper.get_employee_by_id(id)  
                if not all_emp[1]:
                    messages.error(request, "Employee does not exists.")
                    return HttpResponseRedirect(reverse('hr_employee'))

                pic = ''
                pan = ''
                if all_emp[0].picture is None:
                    pic = '/static/crmManager/common/no-photo.png'
                else:
                    pic = all_emp[0].picture.url

                try:
                    pan = all_emp[0].pan_document.url
                except (Exception, ValueError):
                    pass


                all_departments = employee_models.Department.objects.all()
                emp_dep = [data.id for data in all_emp[0].department.all()]
                department_ = []
                status = False
                for data in all_departments:
                    if data.id in emp_dep:
                        status = True
                    department_.append({
                        "status": status,
                        "data": data
                    })
                    status = False

                branch = support_models.Branches.objects.all()
                emp_branch = [data.id for data in all_emp[0].branch.all()]
                branch_ = []
                for data in branch:
                    if data.id in emp_branch:
                        status=True
                    branch_.append({
                        "status": status,
                        "data": data
                    })
                    status = False
                user_type = common.employee_type
                user_type_ = []
                for data in user_type:
                    if data[0] in all_emp[0].user_type:
                        status = True
                    user_type_.append({
                        "status": status,
                        "data": data[0]
                    })
                    status = False
                
                
                salary_info = common_helper.get_employee_salary_details(all_emp[0])
                context.update({"salary_info": salary_info})

                user_data = [{
                    "first_name": all_emp[0].user.first_name,
                    "last_name": all_emp[0].user.last_name,
                    "dob": all_emp[0].date_of_birth,
                    "joined_date": all_emp[0].joined_date,
                    "contact": all_emp[0].contact,
                    "address": all_emp[0].address,
                    "pan": pan,
                    "username": all_emp[0].user.username,
                    "email": all_emp[0].user.email,
                    "staff_head": all_emp[0].staff_head,
                    'pic': pic,
                    "all_departments": department_,
                    "all_branches": branch_,
                    "user_type": user_type_
                }]

                context.update({"emp_data": user_data[0]})

                hrm_access = common_helper.has_hrm_access_to_user(request.user)
                access_val = ""
                if hrm_access[1]:
                    access_val = hrm_access[0].hr_type
                else:
                    access_val = "No"
                context.update({
                    "hrm_access": access_val
                })

                return render(request, "hrm/"+template_version+"/employee_details.html", context=context)
            else:
                messages.error(request, "You dont have access to HRM. Please contact your HR Manager.")
                return HttpResponseRedirect(reverse('crm_index'))
    else:
        messages.error(request, "Sorry. You don't have HRM service activated.")
        return HttpResponseRedirect(reverse('crm_index'))