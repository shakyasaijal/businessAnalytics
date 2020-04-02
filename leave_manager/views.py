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
from notifications import models as notification_models


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
    
    current_branch = cache.get('crm_branch')
    context = {}
    context.update({"current_branch": current_branch})

    leave_type = leave_models.LeaveType.objects.all()

    context.update({"leave_type": leave_type})

    if request.method == "POST":
        if validation.leave_validation(request):
            return HttpResponseRedirect(reverse("crm_index"))

        valid = validation.able_to_apply_leave(request)
        try:
            from_date = datetime.strptime(request.POST['from_date'], "%Y-%m-%d")
            context.update({"old_from_date": from_date})
        except (Exception, ValueError) as e:
            pass
        try:
            to_date = datetime.strptime(request.POST['to_date'], "%Y-%m-%d")
            context.update({"old_to_date": to_date})
        except (Exception, ValueError) as e:
            pass
        try:
            context.update({"old_reason":request.POST['leave_reason']})
        except (Exception, ValueError) as e:
            pass
        try:
            context.update({"old_leave_type":int(request.POST["leave_type"])})
        except (Exception, ValueError) as e:
            pass
        try:
            context.update({"old_half":request.POST['half_leave']})
        except (Exception, ValueError) as e:
            pass

        if not valid[1]:
            context.update({"data_failed": valid[0]})
            return render(request, "leave_manager/"+template_version+"/apply_leave.html", context=context)
            return HttpResponseRedirect(reverse("lms_apply_leave"))

        has_left = validation.has_leave_left(request)
        

        if not has_left[1]:
            if has_left[0]['status'] == "0":
                messages.error(request, "Sorry. You cannot apply for leave. You have {} days of <b>{}</b> leave left.".format(has_left[0]['diff'], has_left[0]['type']))
            elif has_left[0]['status'] == "1":
                messages.error(request, "Sorry. You cannot apply for leave. You have only {} days of <b>{}</b> leave left.".format(has_left[0]['diff'], has_left[0]['type']))
            elif has_left[0]['status'] == "2":
                messages.error(request, "Sorry. Something went wrong. Please try again later.")
            return render(request, "leave_manager/"+template_version+"/apply_leave.html", context=context)
            
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
            full_ = request.user.get_full_name()

            if leave_manager.half_leave_applied(request):
                leave_details.update({"half_day": True, "leave_multiplier": 0.5})

            apply_ = leave_manager.apply_leave(leave_details, request)

            if not apply_[1]:
                messages.error(request, "Leave applied failed. Please try again.")

            notification_models.Notifications.objects.create(employee=issuer, leave=apply_[0], text="{} has applied for {}.".format(full_, leave_models.LeaveType.objects.get(id=request.POST["leave_type"])))
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
        
        return render(request, "leave_manager/"+template_version+"/apply_leave.html", context=context)


@login_required
def lms_index(request):
    if 'crm_branch' not in cache:
        redis.set_crm_branch(request)
    
    current_branch = cache.get('crm_branch')
    context = {}
    context.update({"current_branch": current_branch})
    
    return render(request, "leave_manager/"+template_version+"/index.html", context)


@login_required
def get_leave_requests(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login_view"))

    if not check_leave_admin.is_leave_issuer(request.user):
        messages.error(request, "Sorry. You do not have permission.")
        return HttpResponseRedirect(reverse('lms_index'))
    context = {}
    context.update({"leave_requests": leave_manager.get_leave_requests(request)})

    return render(request, "leave_manager/"+template_version+"/leave-requests.html", context)
