from django.core.cache import cache
from helper.common import redis
from services import models as service_models
from helper.common import manager as helper_manager
from employee import models as employee_models
from notifications import models as notification_models


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
            common_notifications = notification_models.Notifications.objects.filter(employee=None, for_branch=current_branch).order_by('-id')

            for i in notifications:
                if  not i.is_read:
                    count = count+1
                    # if i.leave:
                    #     if i.tag == 'approve/reject':
                    #         data.append({
                    #             'id':i.id,
                    #             'text':i.text,
                    #             'leave_id':i.leave.id,
                    #             'leave_reason':i.leave.reason,
                    #             'from_date':i.leave.from_date,
                    #             'to_date':i.leave.to_date,
                    #             'date':i.date,
                    #             'time':str(i.time).split('.')[0],
                    #             'is_read':i.is_read,
                    #             'leave':True,
                    #             'tag':i.tag,
                    #             'reject_reason':i.leave.reject_reason
                    #         })
                    #     else:
                    #         data.append({
                    #             'id':i.id,
                    #             'text':i.text,
                    #             'leave_id':i.leave.id,
                    #             'leave_reason':i.leave.reason,
                    #             'from_date':i.leave.from_date,
                    #             'to_date':i.leave.to_date,
                    #             'date':i.date,
                    #             'time':str(i.time).split('.')[0],
                    #             'is_read':i.is_read,
                    #             'leave':True,
                    #             'tag':i.tag,
                    #         })
                    # if i.compensation:
                    #     data.append({ 
                    #         'id':i.id,
                    #         'text':i.text,
                    #         'compensation_id':i.compensation.id,
                    #         'leave_reason':i.compensation.reason,
                    #         'days':i.compensation.days,
                    #         'date':i.date,
                    #         'time':str(i.time).split('.')[0],
                    #         'is_read':i.is_read,
                    #         'leave':True,
                    #         'tag':i.tag,
                    #     })  
            for i in common_notifications:
                if  not i.is_read:
                    count = count+1
                    print(i)
                    # if i.holiday:
                    #     data.append({
                    #         'id':i.id,
                    #         'text':'Holiday Notification of ' + i.holiday.title,
                    #         'holiday_title':i.holiday.title,
                    #         'holiday_id':i.holiday.id,
                    #         'from_date':i.holiday.from_date,
                    #         'to_date':i.holiday.to_date,
                    #         'date':i.date,
                    #         'time':str(i.time).split('.')[0],
                    #         'is_read':i.is_read,
                    #         'holiday':True,
                    #         'tag':i.tag,
                    #     })
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
            # data = sorted(data, key = lambda i: (i['date'],i['time']),reverse=True)
            context.update({"cn_count": count})
        except (Exception, employee_models.Employee.DoesNotExist) as e:
            pass

        if total_branch:
            branches = helper_manager.get_current_user_branch(request.user)
            context.update({"total_branch": branches})

        if employee:
            context.update({"context_employee": employee})
    return context
