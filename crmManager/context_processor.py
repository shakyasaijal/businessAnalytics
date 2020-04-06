from django.core.cache import cache
from helper.common import redis
from services import models as service_models
from helper.common import manager as helper_manager
from employee import models as employee_models
from notifications import models as notification_models
from helper.common import manager as helper_manager


def common(request):
    context = {}
    company_info = service_models.service_requested.objects.first()
    if company_info:
        context.update({
            "company_name": company_info.company_name,
        })

    if request.user.is_authenticated:
        if 'crm_branch' not in cache:
            redis.set_crm_branch(request)

        current_branch = cache.get('crm_branch')
        total_branch = helper_manager.user_has_multiple_branch(request.user)
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
            context.update({"cn_count": count})
        except (Exception, employee_models.Employee.DoesNotExist) as e:
            print("Context 1 ",e)
            pass

        try:
            notify = notification_models.NotificationSettings.objects.get_or_create(employee=employee)
            context.update({"show_notify_icon": notify[0].show_notification_icon})
        except (Exception) as e:
            pass

        if total_branch:
            branches = helper_manager.get_current_user_branch(request.user)
            context.update({"total_branch": branches})

        if employee:
            context.update({"context_employee": employee})
        context.update({"current_branch":current_branch})
    return context
