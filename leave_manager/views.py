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
from leave_manager.common import check_leave_admin
from helper.common import redis, manager
from lms_user.common import validation as validation
from notifications import models as notification_models
import pusher
from notifications import views as notification_views


import yaml
credential = yaml.load(open('credentials.yaml'), Loader=yaml.FullLoader)

pusher_client = pusher.Pusher(
  app_id= credential['pusher_app_id'],
  key= credential['pusher_key'],
  secret= credential['pusher_secret'],
  cluster= credential['pusher_cluster'],
  ssl= credential['pusher_ssl']
)


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

            # notification_models.Notifications.objects.create(employee=issuer, leave=apply_[0], text="{} has applied for {}.".format(full_, leave_models.LeaveType.objects.get(id=request.POST["leave_type"])))
            
            
            notification_data = {
                "type": "apply-leave",
                "data": apply_[0],
                "text": "{} has applied for {}.".format(full_, leave_models.LeaveType.objects.get(id=request.POST["leave_type"])),
                "url": '/lms/leave-requests'
            }
            notification_views.create_notification(request, data=notification_data, for_employee=issuer)
            return HttpResponseRedirect(reverse('lms_apply_leave'))

        else:
            messages.error(request, "Leave not applied. Probably server error or you dont have any leave issuer.")
            return HttpResponseRedirect(reverse('crm_index'))
    else:
        
        return render(request, "leave_manager/"+template_version+"/apply_leave.html", context=context)


@login_required
def lms_index(request):
    if 'crm_branch' not in cache:
        redis.set_crm_branch(request)
    
    if not manager.has_lms_access(request.user)[1]:
        messages.error(request, "Sorry. You do not have permission for LMS. Please contact your authority.")
        return HttpResponseRedirect(reverse('crm_index'))


    current_branch = cache.get('crm_branch')
    context = {}
    context.update({"current_branch": current_branch})
    
    return render(request, "leave_manager/"+template_version+"/index.html", context)


@login_required
def get_leave_requests(request):
    if 'crm_branch' not in cache:
        redis.set_crm_branch(request)
    
    current_branch = cache.get('crm_branch')
    context = {}
    context.update({"current_branch": current_branch})

    if not manager.has_lms_access(request.user)[1]:
        messages.error(request, "Sorry. You do not have permission for LMS. Please contact your authority.")
        return HttpResponseRedirect(reverse('crm_index'))

    if not check_leave_admin.is_leave_issuer(request.user):
        messages.error(request, "Sorry. You do not have permission.")
        return HttpResponseRedirect(reverse('lms_index'))
    context.update({"leave_requests": leave_manager.get_leave_requests(request)})

    return render(request, "leave_manager/"+template_version+"/leave-requests.html", context)


@login_required
def approve_leave(request):
    if not manager.has_lms_access(request.user)[1]:
        messages.error(request, "Sorry. You do not have permission for LMS. Please contact your authority.")
        return HttpResponseRedirect(reverse('crm_index'))

    if not check_leave_admin.is_leave_issuer(request.user):
        messages.error(request, "Sorry. You do not have permission.")
        return HttpResponseRedirect(reverse('lms_index'))
        
    id = ''
    if request.method == "POST":
        try:
            id = request.POST['lms_id']
        except (Exception, ValueError) as e:
            print(e)
            messages.error(request, "Something went wrong. Please try again.")
            return HttpResponseRedirect(reverse('lms_index'))
        if leave_manager.approve_leave_request(request, int(id)):
            leave = leave_models.Leave.objects.get(id=int(id))
            notification_data = {
                "type": "leave-approved",
                "data": leave,
                "text": "Your {} has been approved by {}". format(leave.type.type, request.user.get_full_name())
            }
            notification_views.create_notification(request, data=notification_data, for_employee=leave.user.employee)
            total_noti = notification_views.notification_count(request)
            
            pusher_client.trigger('leave-channel', 'leave-approved', {"count": total_noti, "applied_by_id": leave.user.employee.user.id})

            messages.success(request, "Leave approved successfully.")
        else:
            messages.error(request, "Something went wrong. Please try again.")
        return HttpResponseRedirect(reverse('get_leave_requests'))
    else:
        messages.error(request, 'Method not allowed. Please try again. Thank You')
        return HttpResponseRedirect(reverse('lms_index'))


@login_required
def reject_leave(request):
    if not manager.has_lms_access(request.user)[1]:
        messages.error(request, "Sorry. You do not have permission for LMS. Please contact your authority.")
        return HttpResponseRedirect(reverse('crm_index'))

    if not check_leave_admin.is_leave_issuer(request.user):
        messages.error(request, "Sorry. You do not have permission.")
        return HttpResponseRedirect(reverse('lms_index'))

    id = ''
    if request.method == "POST":
        try:
            id = request.POST['lms_id']
        except (Exception, ValueError) as e:
            print(e)
            messages.error(request, "Something went wrong. Please try again.")
            return HttpResponseRedirect(reverse('lms_index'))

        try:
            reject_reason = request.POST['reject_reason']
            if len(reject_reason) < 1:
                messages.error(request, "Rejection Reason of Leave Request is required. Thank You.")
                return HttpResponseRedirect(reverse('get_leave_requests'))
        except (Exception, ValueError) as e:
            print(e)
            messages.error(request, "Rejection Reason of Leave Request is required. Thank You.")
            return HttpResponseRedirect(reverse('get_leave_requests'))

        if leave_manager.reject_leave_request(request, int(id)):
            leave = leave_models.Leave.objects.get(id=int(id))
            notification_data = {
                "type": "leave-rejected",
                "data": leave,
                "text": "Your {} has been rejected by {}". format(leave.type.type, request.user.get_full_name())
            }
            notification_views.create_notification(request, data=notification_data, for_employee=leave.user.employee)
            total_noti = notification_views.notification_count(request)
            
            pusher_client.trigger('leave-channel', 'leave-approved', {"count": total_noti, "applied_by_id": leave.user.employee.user.id})

            messages.success(request, "Leave rejection successfully.")
        else:
            messages.error(request, "Something went wrong. Please try again.")

        return HttpResponseRedirect(reverse('get_leave_requests'))
    else:
        messages.error(request, 'Method not allowed. Please try again. Thank You')
        return HttpResponseRedirect(reverse('lms_index'))


@login_required
def generate_report(request):
    if not manager.has_lms_access(request.user)[1]:
        messages.error(request, "Sorry. You do not have permission for LMS. Please contact your authority.")
        return HttpResponseRedirect(reverse('crm_index'))

    if not check_leave_admin.is_leave_issuer(request.user):
        messages.error(request, "Sorry. You do not have permission.")
        return HttpResponseRedirect(reverse('lms_index'))

    context = {}
    
    if request.method == "POST":
        from_date = datetime.datetime.strptime(
            request.POST["from_date"], "%Y-%m-%d"
        ).date()
        to_date = datetime.datetime.strptime(request.POST["to_date"], "%Y-%m-%d").date()
        leave_list = leave_manager.get_users_leaveDetailFor_searchEngine(
            request.user, from_date, to_date
        )
        if leave_list == {}:
            context.update({"reports": " "})
        else:
            context.update({"reports": sorted(leave_list.items())})
        context.update({"from_date": from_date})
        context.update({"to_date": to_date})
        return render(request, "leave_manager/"+template_version+"/leave-report.html", context)

    else:
        return render(request, "leave_manager/"+template_version+"/leave-report.html", context)
