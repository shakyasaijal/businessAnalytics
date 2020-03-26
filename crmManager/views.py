import requests
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
import datetime
from pprint import pprint
from helper.common import manager as helper_manager
from support import models as support_models
from django.shortcuts import redirect
from leave_manager.common import users
from leave_manager.common import leave_manager


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
    branch = helper_manager.get_current_user_branch(request.user)

    return redirect('crm_branch', slug=branch[0].slug)


@login_required
def crm_branch(request, slug):
    try:
        branch = support_models.Branches.objects.get(slug=slug)
        employees = helper_manager.get_new_employee_by_branch(branch)
        context = {}
        context.update({"new_employee": employees})
        context.update({"current_branch": branch})
        weather_data = get_weather_data()
        context.update({"weather_data":weather_data[0]})

        upcoming_bday = users.get_birthday_today(branch)["upcoming"]
        context.update({"upcoming_bday": upcoming_bday})
        
        holidays = leave_manager.get_holidays(request)
        print(holidays)
        context.update({"holidays": holidays})

        return render(request, "crmManager/"+template_version+"/index.html", context=context)
    except (Exception, support_models.Branches.DoesNotExist) as e:
        print(" No branch slug ", e)
        return HttpResponseRedirect(reverse('crm_index'))