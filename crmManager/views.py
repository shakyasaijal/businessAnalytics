import requests
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.models import Q
import datetime
from django.db.models import Count
from pprint import pprint
from helper.common import manager as helper_manager
from support import models as support_models
from django.shortcuts import redirect
from leave_manager.common import users
from leave_manager.common import leave_manager
from services import models as services_model
from django.core.cache import cache

from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
CACHE_MAX_TTL = getattr(settings, 'CACHE_MAX_TTL', DEFAULT_TIMEOUT)


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