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
from notifications import models as notification_models

from django.core.cache import cache
from django.conf import settings
from helper.common import redis
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page

CACHE_TTL = getattr(settings, 'CACHE_TTL', settings.CACHE_TTL)
CACHE_MAX_TTL = getattr(settings, 'CACHE_MAX_TTL', settings.CACHE_MAX_TTL)


import yaml
credential = yaml.load(open('credentials.yaml'), Loader=yaml.FullLoader)

template_version = ''
try:
    template_version = credential['template_version']
except Exception as e:
    template_version = 'v1'

def get_weather_data(city="Lalitpur"):
    weather_data = []

    try:
        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid='+credential['weather_api']
        r = requests.get(url.format(city)).json()
        if r['cod'] == '404':
            messages.error(request, "City Not Found.")
            return HttpResponseRedirect(reverse('index'))
        city_weather = {
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
            'sunrise': datetime.datetime.fromtimestamp(r['sys']['sunrise']).time().strftime('%H:%M'),
            'sunset': datetime.datetime.fromtimestamp(r['sys']['sunset']).time().strftime('%H:%M'),
            'humidity': r['main']['humidity'],
            'city': r['name']
        }
        weather_data.append(city_weather)
    except Exception as e:
        print(e)

    return weather_data


def weather(request):
    weather_data = get_weather_data(request.POST['city_name'])
    context = {}
    if weather_data:
        context.update({"weather_data": weather_data[0]})
    else:
        weather_data = get_weather_data()
        context.update({"weather_data": weather_data[0]})
        messages.error(request, "City Not Found.")
    
    return render(request, "crmManager/"+template_version+"/index.html", context=context)


@login_required
def crm_index(request):
    weather_data = get_weather_data()

    current_branch = ''
    if 'crm_branch_slug' in cache:
        current_branch = cache.get('crm_branch_slug')
    else:
        branch = helper_manager.get_current_user_branch(request.user)
        current_branch = branch[0].slug

    return redirect('crm_branch', slug=current_branch)


@login_required
def crm_branch(request, slug):
    try:
        branch = support_models.Branches.objects.get(slug=slug)
        
        # Add branch to cache as a global state
        cache.delete('crm_branch')
        cache.set('crm_branch', branch, timeout=CACHE_MAX_TTL)
        cache.delete('crm_branch_slug')
        cache.set('crm_branch_slug', branch.slug, timeout=CACHE_MAX_TTL)

        employees = helper_manager.get_new_employee_by_branch(branch)
        context = {}
        context.update({"new_employee": employees})
        context.update({"current_branch": branch})
        weather_ = ''
        if 'weather' in cache:
            context.update({"weather_data":cache.get('weather')})
        else:
            weather_data = get_weather_data()
            cache.set('weather', weather_data[0], timeout = CACHE_TTL)
            context.update({"weather_data":weather_data[0]})

        upcoming_bday = users.get_birthday_today(branch)["upcoming"]
        context.update({"upcoming_bday": upcoming_bday})
        
        holidays = leave_manager.get_holidays(request, branch)
        context.update({"holidays": holidays})

        return render(request, "crmManager/"+template_version+"/index.html", context=context)
    except (Exception, support_models.Branches.DoesNotExist) as e:
        print(" No branch slug ", e)
        return HttpResponseRedirect(reverse('crm_index'))


@login_required
def help_support(request):
    all_service = services_model.AllServices.objects.values_list('status', flat=True)
    data_ = []
    in_data = []
    context = {}
    for data in all_service:
        serv = services_model.AllServices.objects.filter(status=data)
        for d in serv:
            in_data.append({
                "name": d.service_name,
                "expiry": d.expiry_date
            })
        data_.append({
            data: in_data
        })
        in_data = []
    context.update({"data": data_})
    return render(request, "crmManager/"+template_version+"/help.html", context= context)


def get_notification(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please login.")
        return HttpResponseRedirect(reverse('login_view'))
    try:
        if 'crm_branch' not in cache:
            print("Notification cache xaina")
            redis.set_crm_branch(request)
        current_branch = cache.get('crm_branch')
        data = []
        count = 0
        employee = employee_models.Employee.objects.get(user=request.user)
        notifications = notification_models.Notifications.objects.filter(employee=employee).order_by('-id')
        common_notifications = notification_models.Notifications.objects.filter(employee=None, for_branch=current_branch).order_by('-id')
        for i in notifications:
            if  not i.is_read:
                count = count+1
                if i.leave:
                    if i.tag == 'approve/reject':
                        data.append({
                            'id':i.id,
                            'text':i.text,
                            'leave_id':i.leave.id,
                            'leave_reason':i.leave.reason,
                            'from_date':i.leave.from_date,
                            'to_date':i.leave.to_date,
                            'date':i.date,
                            'time':str(i.time).split('.')[0],
                            'is_read':i.is_read,
                            'leave':True,
                            'tag':i.tag,
                            'reject_reason':i.leave.reject_reason
                        })
                    else:
                        data.append({
                            'id':i.id,
                            'text':i.text,
                            'leave_id':i.leave.id,
                            'leave_reason':i.leave.reason,
                            'from_date':i.leave.from_date,
                            'to_date':i.leave.to_date,
                            'date':i.date,
                            'time':str(i.time).split('.')[0],
                            'is_read':i.is_read,
                            'leave':True,
                            'tag':i.tag,
                        })
                if i.compensation:
                    data.append({ 
                        'id':i.id,
                        'text':i.text,
                        'compensation_id':i.compensation.id,
                        'leave_reason':i.compensation.reason,
                        'days':i.compensation.days,
                        'date':i.date,
                        'time':str(i.time).split('.')[0],
                        'is_read':i.is_read,
                        'leave':True,
                        'tag':i.tag,
                    })  
        for i in common_notifications:
            if  not i.is_read:
                count = count+1
                if i.holiday:
                    data.append({
                        'id':i.id,
                        'text':'Holiday Notification of ' + i.holiday.title,
                        'holiday_title':i.holiday.title,
                        'holiday_id':i.holiday.id,
                        'from_date':i.holiday.from_date,
                        'to_date':i.holiday.to_date,
                        'date':i.date,
                        'time':str(i.time).split('.')[0],
                        'is_read':i.is_read,
                        'holiday':True,
                        'tag':i.tag,
                    })
                # if i.notice:
                #     data.append({
                #         'id':i.id,
                #         'text': i.notice.topic,
                #         'notice_message':i.notice.message,
                #         'date':i.date,
                #         'time':str(i.time).split('.')[0],
                #         'is_read':i.is_read,
                #         'notice':True,
                #         'tag':i.tag,
                #     })                
        data = sorted(data, key = lambda i: (i['date'],i['time']),reverse=True)
        return JsonResponse({"status": True, "data":data}, status=200)
    except (Exception, employee_models.Employee.DoesNotExist) as e:
        print("Notification API Exception", e)
        return JsonResponse({"status": False, "error": "Something went wrong. Please try again later."}, status=500)
