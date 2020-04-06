import yaml
import requests
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.http import JsonResponse
import datetime
from django.db.models import Count
from pprint import pprint
from helper.common import manager as helper_manager
from support import models as support_models
from django.shortcuts import redirect
from leave_manager.common import users
from leave_manager.common import leave_manager
from services import models as services_model
from employee import models as employee_models
from . import models as notification_models

from django.core.cache import cache
from django.conf import settings
from helper.common import redis
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page

CACHE_TTL = getattr(settings, 'CACHE_TTL', settings.CACHE_TTL)
CACHE_MAX_TTL = getattr(settings, 'CACHE_MAX_TTL', settings.CACHE_MAX_TTL)


credential = yaml.load(open('credentials.yaml'), Loader=yaml.FullLoader)

template_version = ''
try:
    template_version = credential['template_version']
except Exception as e:
    template_version = 'v1'


def update_notification_settings(emp):
    try:
        notify = notification_models.NotificationSettings.objects.get(employee=emp)
        notify.show_notification_icon = False
        notify.save()
    except (Exception, notification_models.NotificationSettings.DoesNotExist) as e:
        pass
        print(e)


@login_required
def notifications(request):
    if 'crm_branch' not in cache:
        redis.set_crm_branch(request)

    try:
        current_branch = cache.get('crm_branch')
        context = {}
        context.update({"current_branch": current_branch})
        user_all_branch = helper_manager.get_current_user_branch(request.user)
        data = []
        count = 0
        employee = employee_models.Employee.objects.get(user=request.user)
        notifications = notification_models.Notifications.objects.filter(
            employee=employee).order_by('-id')
        common_notifications = notification_models.Notifications.objects.filter(
            employee=None, for_branch__in=user_all_branch).order_by('-id').distinct()

        for i in notifications:
            symbol = "/static/crmManager/v1/assets/lms.png"
            count = count+1
            if i.leave:
                if not i.is_read:
                    data.append({
                        'id': i.id,
                        'text': i.text,
                        'leave_id': i.leave.id,
                        'leave_reason': i.leave.reason,
                        'from_date': i.leave.from_date,
                        'to_date': i.leave.to_date,
                        'date': i.date,
                        'time': str(i.time).split('.')[0],
                        'is_read': i.is_read,
                        'leave': True,
                        'tag': i.tag,
                        'reject_reason': i.leave.reject_reason,
                        "symbol": symbol,
                        'url': i.url
                    })
                    if i.tag == "approved":
                        i.is_read = True
            if i.compensation:
                if not i.is_read:
                    data.append({
                        'id': i.id,
                        'text': i.text,
                        'compensation_id': i.compensation.id,
                        'leave_reason': i.compensation.reason,
                        'days': i.compensation.days,
                        'date': i.date,
                        'time': str(i.time).split('.')[0],
                        'is_read': i.is_read,
                        'leave': True,
                        'tag': i.tag,
                        "symbol": symbol
                    })
        for i in common_notifications:
            is_read_commmon_status = False
            if employee in i.seen_by.all():
                is_read_commmon_status = True
            else:
                count = count+1
                is_read_commmon_status = False

            symbol = "/static/crmManager/v1/assets/"
            if i.holiday:
                symbol += "holiday.png"
                data.append({
                    'id': i.id,
                    'text': 'Holiday Notification of ' + i.holiday.title,
                    'holiday_title': i.holiday.title,
                    'holiday_id': i.holiday.id,
                    'from_date': i.holiday.from_date,
                    'to_date': i.holiday.to_date,
                    'date': i.date,
                    'time': str(i.time).split('.')[0],
                    'is_read': is_read_commmon_status,
                    'holiday': True,
                    'branch': i.for_branch.all(),
                    'tag': i.tag,
                    "symbol": symbol
                })
                i.seen_by.add(employee)
            # if i.notice:
                # symbol += "notice.png"
            #     data.append({
            #         'id':i.id,
            #         'text': i.notice.topic,
            #         'notice_message':i.notice.message,
            #         'date':i.date,
            #         'time':str(i.time).split('.')[0],
            #         'is_read':i.is_read,
            #         'notice':True,
            #         'tag':i.tag,
                # "symbol": symbol
            #     })
        # data = sorted(data, key=lambda i: (i['date'], i['time']), reverse=True)
        context.update({"data": data})
        context.update({"count": count})

        update_notification_settings(employee)
        return render(request, "notifications/"+template_version+"/notifications.html", context)
    except (Exception, employee_models.Employee.DoesNotExist) as e:
        print("Notification API Exception", e)
        return HttpResponseRedirect(reverse('crm_index'))



def notification_count(request):
    employee = employee_models.Employee.objects.none()
    data = []
    count = 0
    try:
        employee = employee_models.Employee.objects.get(user=request.user)
        notifications = notification_models.Notifications.objects.filter(employee=employee).order_by('-id')
        user_all_branch = helper_manager.get_current_user_branch(request.user)
        common_notifications = notification_models.Notifications.objects.filter(employee=None, for_branch__in=user_all_branch).order_by('-id').distinct()
        for i in notifications:
            count = count+1
        for i in common_notifications:
            if employee not in i.seen_by.all():
                count = count+1
        return count
    except (Exception, employee_models.Employee.DoesNotExist) as e:
        print("Context 1 ",e)
        return count
        

def create_notification(request, data, for_employee=""):

    if data["type"] == "leave-approved":
        if notification_models.Notifications.objects.create(leave=data['data'], text=data['text'], employee=for_employee, tag="approved"):
            return True
        else:
            return False

    elif data["type"] == "apply-leave":
        if notification_models.Notifications.objects.create(employee=for_employee, leave=data["data"], text=data["text"], url=data['url'], tag=data["data"].id):
            return True
        return False

    elif data["type"] == "leave-rejected":
        if notification_models.Notifications.objects.create(leave=data['data'], text = data['text'], employee=for_employee, tag="rejected"):
            return True
        else:
            return False
            