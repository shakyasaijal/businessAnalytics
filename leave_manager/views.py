from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.urls import reverse
from django.http import HttpResponseRedirect
from datetime import datetime
from leave_manager.common import leave_manager
from leave_manager import models as leave_models
from  leave_manager.common import check_leave_admin
from helper.common import redis
from lms_user.common import validation as validation


import yaml
credential = yaml.load(open('credentials.yaml'), Loader=yaml.FullLoader)

template_version = ''
try:
    template_version = credential['template_version']
except Exception as e:
    template_version = 'v1'


@login_required
def apply_leave(request):
    if 'crm_branch' not in cache:
        redis.set_crm_branch(request)
    
    
    if request.method == "POST":
        if validation.leave_validation(request):
            return HttpResponseRedirect(reverse("crm_index"))

        valid = validation.able_to_apply_leave(request)

        print(valid )

        if not valid[1]:
            context = {}
            context.update({"data_failed": valid[0]})
            return render(request, "leave_manager/"+template_version+"/apply_leave.html", context=context)
            return HttpResponseRedirect(reverse("lms_apply_leave"))

        leave_issuer = check_leave_admin.get_employee_leave_issuer(request.user)
        if leave_issuer[1]:
            issuer = leave_issuer[0]
            current_lms_user = leave_manager.get_lms_user(request.user)

            if not current_lms_user[1]:
                messages.error(request, "Something went wrong. Please try again.")
                return HttpResponseRedirect(reverse("crm_index"))
                
            leave_details = {
                "current_lms_user": current_lms_user[0],
                "issuer": issuer,
                "from_date": datetime.strptime(request.POST["from_date"], "%Y-%m-%d"),
                "to_date": datetime.strptime(request.POST["to_date"], "%Y-%m-%d"),
                "leave_type": leave_models.LeaveType.objects.get(id=request.POST["leave_type"]),
                "leave_reason": request.POST["leave_reason"],
                "half_day": False,
                "leave_multiplier": 1,
            }

            if leave_manager.half_leave_applied(request):
                leave_details.update({"half_day": True, "leave_multiplier": 0.5})

            if not leave_manager.apply_leave(leave_details, request):
                messages.error(request, "Leave applied failed. Please try again.")

            return HttpResponseRedirect(reverse('lms_apply_leave'))

        else:
            messages.error(request, "Leave not applied. Probably server error or you dont have any leave issuer.")
            return HttpResponseRedirect(reverse('crm_index'))


        leave_details = {
            "from_date": datetime.strptime(request.POST["from_date"], "%Y-%m-%d"),
            "to_date": datetime.strptime(request.POST["to_date"], "%Y-%m-%d"),
            "leave_type": leave_models.LeaveType.objects.get(id=request.POST["leave_type"]),
            "half_day": False,
            "leave_multiplier": 1
        }
        
        if leave_manager.half_leave_applied(request=request):
            leave_details.update({"half_day": True, "leave_multiplier": 0.5})
    else:
        current_branch = cache.get('crm_branch')
        context = {}
        context.update({"current_branch": current_branch})
        leave_type = leave_models.LeaveType.objects.all()
        context.update({"leave_type": leave_type})
        return render(request, "leave_manager/"+template_version+"/apply_leave.html", context=context)

