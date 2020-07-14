from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from pprint import pprint
from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
from helper.common import redis
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from helper import management
from . import forms
from notifications import models as notification_models
from helper.common import manager as helper_manager


CACHE_TTL = getattr(settings, 'CACHE_TTL', settings.CACHE_TTL)
CACHE_MAX_TTL = getattr(settings, 'CACHE_MAX_TTL', settings.CACHE_MAX_TTL)


import yaml
credential = yaml.load(open('credentials.yaml'), Loader=yaml.FullLoader)

template_version = ''
try:
    template_version = credential['template_version']
except Exception as e:
    template_version = 'v1'


@login_required
def add_holidays(request):
    has_access = management.can_crud_holidays(request.user)
    if not has_access:
        messages.error(request, "Sorry. You do not have an access.")
        return HttpResponseRedirect(reverse('crm_index'))

    if request.method == "POST":
        form = forms.HolidayForm(request.POST)
        if form.is_valid():
            instance = form.save()
            try:
                notify = request.POST['notify_all']
                if notify:
                    now = notification_models.Notifications.objects.create(text="Holiday for {} has been added.".format(form.cleaned_data['title']), holiday=instance)
                    now.for_branch.set(form.cleaned_data["branch"])
                    now.save()
                    for data in form.cleaned_data['branch']:
                        emp = helper_manager.get_all_employee_by_branch(data)
                        for d in emp:
                            notification_models.NotificationSettings.objects.filter(employee=d).update(show_notification_icon=True)
            except (Exception, ValueError) as e:
                print(e)
                pass
            form = forms.HolidayForm()
            messages.success(request,"Holiday Successfully Added.")
            return HttpResponseRedirect(reverse('crm_index'))
        else:
            messages.error(request, "Failed to add new holiday. Please try again.")
            return render(request, "management/"+template_version+"/holidays/add.html", context = {'form': form})
    else:
        form = forms.HolidayForm()
        return render(request, "management/"+template_version+"/holidays/add.html", context = {'form': form})
