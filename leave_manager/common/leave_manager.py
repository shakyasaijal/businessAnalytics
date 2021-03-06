import calendar
from lms_user.models import LmsUser
from django.urls import reverse_lazy
from datetime import datetime, timedelta, date
from leave_manager import models as leave_models
from leave_manager.common.send_email_notification import send_email_notification
# from mobile_api.common.fcm import fcm
from lms_user import models as lms_user_models
from django.contrib import messages
from employee import models as employee_models
from leave_manager.common.send_email_notification import send_email_notification
from services import models as service_models
from collections import Counter
import pusher
import yaml
from leave_manager.common import check_leave_admin
from notifications import models as notification_models


credentials = yaml.load(open('credentials.yaml'), Loader=yaml.FullLoader)
pusher_client = pusher.Pusher(
  app_id= credentials['pusher_app_id'],
  key= credentials['pusher_key'],
  secret= credentials['pusher_secret'],
  cluster= credentials['pusher_cluster'],
  ssl= credentials['pusher_ssl']
)


def get_lms_user(user):
    try:
        emp = employee_models.Employee.objects.get(user=user)
        lms = LmsUser.objects.get(employee=emp)
        return lms, True
    except (Exception) as e:
        return '', False


def leave_days(leave_details, request):
    days = ((leave_details['to_date'] - leave_details['from_date']).days+1) * leave_details['leave_multiplier']

    weekdays = Counter()
    from_date = datetime.strptime(request.POST['from_date'], "%Y-%m-%d")
    to_date = datetime.strptime(request.POST['to_date'], "%Y-%m-%d")

    for i in range((to_date - from_date).days+1):
        weekdays[(from_date + timedelta(i)).strftime('%a')] += 1

    sat = False
    deduct = weekdays['Sat']

    if leave_details['half_day']:
        deduct = deduct/2

    if weekdays['Sat'] > 0:
        days = days-deduct
        sat = True

    return {"days": days, 'sat': sat, 'weekdays':weekdays['Sat'], 'deduct': deduct}


def apply_leave(leave_details, request):
    try:
        leave_days_data = leave_days(leave_details, request)
        sat = leave_days_data['sat']
        weekdays = leave_days_data['weekdays']
        deduct = leave_days_data['deduct']
        days = leave_days_data['days']
        reason = ''
        if sat:
            day_or_days = "day"
            if weekdays > 1:
                day_or_days = "days"
            reason += "There are {} {} of Saturday.".format(weekdays, day_or_days)

        leave = leave_models.Leave.objects.create(
            user=leave_details['current_lms_user'], type=leave_details['leave_type'], from_date=leave_details['from_date'],
            to_date=leave_details['to_date'], half_day=leave_details['half_day'], reason=leave_details['leave_reason'],
            days=days, leave_on_holiday=deduct, leave_on_holiday_reason=reason)
        if leave:
            service_ = service_models.service_requested.objects.first()
            domain = service_.domain
            email_details = {
                'recipient_email': leave_details['issuer'].user.email,
                'email_subject': 'LMS | A new leave request has arrived',
                'email_body': '''
                            Hi {}, A new leave Request has arrived.
                            From: {}
                            Leave Type: {}
                            Half Day: {}
                            Days: {}
                            Leave Reason: {}
                            URL: {}
                            '''.format(leave_details['issuer'].user.get_full_name(), leave_details['current_lms_user'].employee.user.get_full_name(),
                                       leave_details['leave_type'], leave_details['half_day'], days, leave_details['leave_reason'], 'http://{}{}'.format(request.META['HTTP_HOST'],
                                                                                                                                                         reverse_lazy('lms_apply_leave')))
            }
            if send_email_notification(update_details=email_details):
                if sat:
                    messages.success(
                        request, "Leave applied successfully. Your {} day of Saturday will not be deducted from your leave.".format(deduct))
                else:
                    messages.success(request, "Leave applied successfully.")

                notification_models.NotificationSettings.objects.filter(employee=leave_details['issuer']).update(show_notification_icon=True)
                pusher_client.trigger('leave-channel', 'leave-approve', {'applied_by': 'hello world', 'applied_to_id': leave_details['issuer'].user.id,"main-data":{"msg": "{} has applied for {}".format(leave_details['current_lms_user'].employee.user.get_full_name(), leave_details['leave_type']), "date": "Recently"}, 'message': 'New leave applied by {}'.format(leave_details['current_lms_user'].employee.user.get_full_name())})
                return leave, True
            else:
                leave.delete()
                return '', False
        else:
            return '', False
    except (Exception) as e:
        print("leave_manager > common > leave_manager > line 86 ", e)
        if leave:
            leave.delete()
            return '', False


def half_leave_applied(request):
    try:
        if int(request.POST['half_leave']) == 1:
            return True
    except Exception as e:
        print(e)
        return False
    return False


def get_leave_requests_by_id(user, id):
    pending_leave_requests = []
    my_leave_approvees = LmsUser.objects.filter(leave_issuer=user)

    for leave_request in Leave.objects.filter(user__in=my_leave_approvees, leave_pending=True, id=id):
        leave_multiplier = 1
        if leave_request.half_day:
            leave_multiplier = 0.5
        pending_leave_requests.append(
            {
                'id': leave_request.id,
                'full_name': leave_request.user.user.get_full_name(),
                'department': leave_request.user.department.department,
                'from_date': str(leave_request.from_date),
                'to_date': str(leave_request.to_date),
                'total_days': ((leave_request.to_date - leave_request.from_date).days + 1) * leave_multiplier,
                'leave_type': leave_request.type.type,
                'leave_reason': leave_request.reason,
                'half_day': leave_request.half_day,
            }
        )
    return pending_leave_requests


def get_leave_requests(request):
    pending_leave_requests = []
    try:
        emp = employee_models.Employee.objects.get(user=request.user)
        my_leave_approvees = lms_user_models.LmsUser.objects.filter(leave_issuer=emp)

        for leave_request in leave_models.Leave.objects.order_by("-id").filter(user__in=my_leave_approvees, leave_pending=True):
            if leave_request.from_date >= date.today():
                leave_multiplier = 1
                if leave_request.half_day:
                    leave_multiplier = 0.5
                pending_leave_requests.append(
                    {
                        'id': leave_request.id,
                        'full_name': leave_request.user.employee.user.get_full_name(),
                        'picture': leave_request.user.employee.picture.url,
                        'department': leave_request.user.employee.department.all(),
                        'from_date': leave_request.from_date,
                        'to_date': leave_request.to_date,
                        'total_days': leave_request.days,
                        'leave_type': leave_request.type.type,
                        'leave_reason': leave_request.reason,
                        'half_day': leave_request.half_day,
                        'notification': leave_request.notification,
                        "leave_on_holiday": leave_request.leave_on_holiday,
                        "leave_on_holiday_reason":leave_request.leave_on_holiday_reason,
                        "multiplied": leave_request.days*2
                    }
                )
        return pending_leave_requests
    except (Exception, employee_models.Employee.DoesNotExist) as e:
        print(e)
        return pending_leave_requests


def get_leave_today():
    leaves_today = []
    for leave_request in Leave.objects.filter(from_date__lte=datetime.today(), to_date__gte=datetime.today(),
                                              leave_pending=False, leave_approved=True):

        try:
            image = leave_request.user.image.url.split('/static/')[1]
        except Exception as e:
            print(e)
            image = '/lms_user/images/photograph.png'

        leaves_today.append({
            'id': leave_request.id,
            'full_name': leave_request.user.user.get_full_name(),
            'image': image,
            'department': leave_request.user.department.department,
            'from_date': str(leave_request.from_date),
            'to_date': str(leave_request.to_date),
            'leave_type': leave_request.type.type,
            'leave_reason': leave_request.reason,
            'half_day': leave_request.half_day,
        })
    return leaves_today


def get_leave_detail(leave):
    try:
        half = "No"
        if leave.half_day:
            half = "Yes"
        leave_detail = {
            'id': leave.id,
            'lms_user': leave.user,
            'total_days': leave.days,
            'leave_type': leave.type.type,
            'leave_reason': leave.reason,
            'half_day': half,
        }
        return leave_detail
    except Exception as e:
        print('Could not Get Leave Detail', e)
        return {}


def get_leave_count_monthly(leave, month):
    if leave.from_date.month == leave.to_date.month:
        return leave.to_date.day - leave.from_date.day + 1
    elif leave.from_date.month == month:
        return calendar.monthrange(leave.from_date.year, leave.from_date.month)[1] - leave.from_date.day + 1
    else:
        return leave.to_date.day


def get_user_leave_detail_monthly(lms_user_id, month, user):
    user_detail = {}
    try:
        monthly_leave = []
        lms_user = LmsUser.objects.get(id=lms_user_id)
        user_detail.update({
            'full_name': lms_user.user.get_full_name(),
            'leaves': monthly_leave,
        })

        if LmsUser.objects.filter(leave_issuer=user):
            leaves = get_monthly_leave_detail_of_all_user_by_month(month, user)
        else:
            leaves = get_monthly_leave_detail_by_id_month(lms_user_id, month)

        for leave in leaves:
            monthly_leave.append({
                'name': leave.user,
                'leave_type': leave.type.type,
                'from_date': leave.from_date,
                'to_date': leave.to_date,
                'days': get_leave_count_monthly(leave, month),
                'id': leave.id,
                'leave_pending': leave.leave_pending,
                'leave_approved': leave.leave_approved
            })
        user_detail.update({
            'leaves': monthly_leave
        })

        return user_detail
    except Exception as e:
        print(e)
        return user_detail


def get_own_leave_detail_monthly(lms_user_id, month):
    user_detail = {}
    try:
        monthly_leave = []
        lms_user = LmsUser.objects.get(id=lms_user_id)
        approved = 0.0
        rejected = 0.0
        user_detail.update({
            'full_name': lms_user.user.get_full_name(),
            'leaves': monthly_leave,
            'approved': approved,
            'rejected': rejected
        })
        leaves = get_monthly_leave_detail_by_id_month(lms_user_id, month)
        for leave in leaves:
            leave_multiplier = 1
            if leave.half_day:
                leave_multiplier = 0.5
            if not leave.leave_pending and not leave.leave_approved:
                rejected += 1
            if leave.leave_approved:
                approved += 1
            monthly_leave.append({
                'name': leave.user,
                'leave_type': leave.type.type,
                'from_date': leave.from_date,
                'to_date': leave.to_date,
                'days':  ((leave.to_date - leave.from_date).days + 1) * leave_multiplier,
                'id': leave.id,
                'leave_pending': leave.leave_pending,
                'leave_approved': leave.leave_approved,
                'reject_reason': leave.reject_reason,
                'leave_reason': leave.reason,
                'half_day': leave.half_day,
            })
        user_detail.update({
            'leaves': monthly_leave,
            'approved': approved,
            'rejected': rejected
        })

        return user_detail
    except Exception as e:
        print(e)
        return user_detail


def approve_leave_request(request, leave_id):
    try:
        leave = leave_models.Leave.objects.get(id=leave_id)
        leave.leave_pending = False
        leave.leave_approved = True
        leave_detail = get_leave_detail(leave)
        user = leave_detail['lms_user']

        update_details = {
            'recipient_email': user.employee.user.email,
            'email_subject': 'LMS | Your Leave Request Has Been Approved',
            'email_body': '''
            Hi {}, Your Leave Request Has just been approved by {}.
            Leave Type: {}
            Half Leave: {}
            Days: {}
            Leave Reason {}
            '''.format(user.employee.user.get_full_name(), request.user.get_full_name(), leave_detail['leave_type'],
                       leave_detail['half_day'],
                       leave_detail['total_days'], leave_detail['leave_reason'])
        }
        leave.leave_pending = False
        leave.leave_approved = True

        leave.save()
        notification_models.NotificationSettings.objects.filter(employee = user.employee).update(show_notification_icon=True)

        try:
            leave_issuer_fcm = user.fcm_token
            fcm(leave_issuer_fcm, request.user.get_full_name(),
                leave.id, "approve_leave")
        except Exception as e:
            print(e, 'asdf')

        if send_email_notification(update_details=update_details):
            return True
        else:
            return False
    except (leave_models.Leave.DoesNotExist, Exception) as e:
        print(e)
        return False


def reject_leave_request(request, leave_id):
    try:
        leave = leave_models.Leave.objects.get(id=leave_id)
        leave_detail = get_leave_detail(leave)
        user = leave_detail['lms_user']
        leave.leave_pending = False
        leave.leave_approved = False
        leave.reject_reason = request.POST['reject_reason']
        update_details = {
            'recipient_email': user.employee.user.email,
            'email_subject': 'LMS | Your Leave Request Has Been Rejected',
            'email_body': '''
                    Hi {}, Your Leave Request Has just been rejected by {}.
                    Leave Type: {}
                    Half Leave: {}
                    Days: {}
                    Leave Reason {}
                    '''.format(user.employee.user.get_full_name(), request.user.get_full_name(), leave_detail['leave_type'],
                               leave_detail['half_day'],
                               leave_detail['total_days'], leave_detail['leave_reason'])
        }

        try:
            leave_issuer_fcm = user.fcm_token
            fcm(leave_issuer_fcm, request.user.get_full_name(),
                leave.id, "reject_leave")
        except Exception as e:
            print(e)
        if send_email_notification(update_details=update_details):
            leave.save()
            return True
        else:
            leave.leave_pending = True
            leave.reject_reason = ''
            leave.save()
            return False
    except (leave_models.Leave.DoesNotExist, Exception) as e:
        print(e)
        return False


def get_monthly_leave_detail_by_id_month(lms_user_id, month):
    leave_list = Leave.objects.order_by(
        "-id").filter(from_date__month__gte=4, user__id=lms_user_id)
    leave = []
    for leaves in leave_list:
        if leaves.from_date.month == 4:
            if (leaves.from_date.day < 14 and leaves.to_date.day >= 14) or leaves.from_date.day >= 14:
                leave.append(leaves)
        else:
            leave.append(leaves)
    return leave


def get_monthly_compensationLeave_detail(lms_user_id, month):
    leave = Leave.objects.order_by(
        "-id").filter(from_date__month=month, user__id=lms_user_id)
    return leave


def get_monthly_leave_detail_of_all_user_by_month(month, user):
    # leave = Leave.objects.order_by("-id").filter(from_date__month=month)
    my_leave_approvees = LmsUser.objects.filter(leave_issuer=user)
    leave = Leave.objects.order_by(
        "-id").filter(user__in=my_leave_approvees, from_date__month=month)
    return leave


def get_monthly_compensationLeave_detail_of_all_user(user):
    my_leave_approvees = LmsUser.objects.filter(leave_issuer=user)
    leave = CompensationLeave.objects.order_by(
        "-id").filter(user__in=my_leave_approvees)
    return leave


def get_holidays(request, branch):
    holidays = leave_models.Holiday.objects.all().order_by("-from_date")
    company_holidays = []
    for holiday in holidays:
        delta = holiday.from_date - date.today()
        holiday_branch = holiday.branch.all()
        if len(holiday_branch) < 1 or branch in holiday_branch:
            company_holidays.append({
                'id': holiday.id,
                'title': holiday.title,
                'from_date': holiday.from_date,
                'to_date': holiday.to_date,
                'days_remaining': delta.days,
                'description': holiday.description,
                'days': get_totalDays_ofEach_holidays(holiday.from_date, holiday.to_date),
            })
        else:
            pass
        holiday_branch = None
    return company_holidays[:2]


def get_all_holidays(request):
    holidays = Holiday.objects.all()
    company_holidays = []
    for holiday in holidays:
        image_url = get_image_url(None, request, 'holiday', holiday.id)
        delta = holiday.from_date - date.today()

        from_date_month = holiday.from_date.month
        from_date_day = holiday.from_date.day

        if from_date_month < 10:
            from_date_month = "0" + str(holiday.from_date.month)
        if from_date_day < 10:
            from_date_day = "0" + str(holiday.from_date.day)

        from_date_formatted = (
            str(holiday.from_date.year)
            + "-"
            + str(from_date_month)
            + "-"
            + str(from_date_day)
        )

        to_date_month = holiday.to_date.month
        to_date_day = holiday.to_date.day

        if to_date_month < 10:
            to_date_month = "0" + str(holiday.to_date.month)
        if to_date_day < 10:
            to_date_day = "0" + str(holiday.to_date.day)

        to_date_formatted = (
            str(holiday.to_date.year)
            + "-"
            + str(to_date_month)
            + "-"
            + str(to_date_day)
        )

        company_holidays.append({
            'id': holiday.id,
            'title': holiday.title,
            'from_date': holiday.from_date,
            'to_date': holiday.to_date,
            'days_remaining': delta.days,
            'description': holiday.description,
            'image': image_url,
            'days': get_totalDays_ofEach_holidays(holiday.from_date, holiday.to_date),
            'from_date_formatted': from_date_formatted,
            'to_date_formatted': to_date_formatted
        })
    return company_holidays


def get_totalDays_ofEach_holidays(from_date, to_date):
    delta = to_date-from_date
    return delta.days+1


def get_all_leaves_unseen():
    leave = Leave.objects.filter(notification=True).count()
    print(leave)
    return leave


def apply_CompensationLeave(**kwargs):
    leave_details = kwargs['leave_details']
    request = kwargs['request']
    try:
        leave = CompensationLeave.objects.create(
            reason=leave_details['leave_reason'],
            days=leave_details['days'],
            user=leave_details['user']
        )
        update_details = {
            'recipient_email': leave_details['issuer'].email,
            'email_subject': 'LMS | A new Leave Request Has Arrived ',
            'email_body': '''
                    Hi {}, A new compensation leave Request has arrived.
                    From: {}
                    Leave Reason: {}
                    Days: {}
                    URL: {}
                    '''.format(leave_details['issuer'].get_full_name(), leave_details['user'].user.get_full_name(),
                               leave_details['leave_reason'], leave_details['days'],
                               'http://{}{}'.format(request.META['HTTP_HOST'],
                                                    reverse_lazy('leave_manager_leave_requests')))
        }
        try:
            user = lms_user_models.LmsUser.objects.get(user=request.user)
            leave_issuer = lms_user_models.LmsUser.objects.get(
                user=leave_details['issuer'])
            leave_issuer_fcm = leave_issuer.fcm_token
            fcm(leave_issuer_fcm, user, leave.id, "compensation_apply")
        except (lms_user_models.LmsUser.DoesNotExist, Exception) as e:
            print(e)
        if send_email_notification(update_details=update_details):
            return True
        else:
            leave.delete()
            return False
    except Exception as e:
        print(e)
        return False


def get_compensationLeave_requests(user):
    pending_leave_requests = []
    my_leave_approvees = LmsUser.objects.filter(leave_issuer=user)
    for leave_request in CompensationLeave.objects.order_by("-id").filter(user__in=my_leave_approvees, leave_pending=True):
        pending_leave_requests.append(
            {
                'id': leave_request.id,
                'full_name': leave_request.user.user.get_full_name(),
                'department': leave_request.user.department.department,
                'leave_reason': leave_request.reason,
                'days': leave_request.days,
                'notification': leave_request.notification
            }
        )
    return pending_leave_requests


def get_compensationLeave_requests_by_id(user, id):
    pending_leave_requests = []
    my_leave_approvees = LmsUser.objects.filter(leave_issuer=user)
    for leave_request in CompensationLeave.objects.filter(user__in=my_leave_approvees, leave_pending=True, id=id):
        pending_leave_requests.append(
            {
                'id': leave_request.id,
                'full_name': leave_request.user.user.get_full_name(),
                'department': leave_request.user.department.department,
                'days': leave_request.days,
                'leave_reason': leave_request.reason,
            }
        )
    return pending_leave_requests


def reject_compensationLeave_request(request, leave_id):
    try:
        leave = CompensationLeave.objects.get(id=leave_id)
        print(leave)
        leave_detail = get_compensationLeave_detail(leave)
        user = leave_detail['lms_user']
        leave.leave_pending = False
        leave.leave_approved = False
        update_details = {
            'recipient_email': user.user.email,
            'email_subject': 'LMS | Your Compensation Leave Request Has Been Rejected',
            'email_body': '''
                    Hi {}, Your Leave Request Has just been rejected by {}.
                    Days: {}
                    Leave Reason: {}
                    '''.format(user.user.get_full_name(), request.user.get_full_name(),
                               leave_detail['days'], leave_detail['leave_reason'])
        }
        leave.save()
        try:
            leave_issuer_fcm = user.fcm_token
            fcm(leave_issuer_fcm, request.user.get_full_name(),
                leave.id, "reject_compensation")
        except Exception as e:
            print(e)

        if send_email_notification(update_details=update_details):
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def get_compensationLeave_detail(leave):
    try:
        leave_detail = {
            'id': leave.id,
            'lms_user': leave.user,
            'department': leave.user.department.department,
            'days': leave.days,
            'leave_reason': leave.reason,
        }
        return leave_detail
    except Exception as e:
        print('Could not Get Compensation Leave Detail', e)
        return {}


def approve_compensationLeave_request(request, leave_id):
    try:
        leave = CompensationLeave.objects.get(id=leave_id)
        leave.leave_pending = False
        leave.leave_approved = True
        leave_detail = get_compensationLeave_detail(leave)
        user = leave_detail['lms_user']
        user.compensation_leave += leave_detail['days']

        update_details = {
            'recipient_email': user.user.email,
            'email_subject': 'LMS | Your Compensation Leave Request Has Been Approved',
            'email_body': '''
            Hi {}, Your Leave Request Has just been approved by {}.
            Days: {}
            Leave Reason {}
            '''.format(user.user.get_full_name(), request.user.get_full_name(),
                       leave_detail['days'], leave_detail['leave_reason'])
        }
        user.save()
        leave.save()
        try:
            leave_issuer_fcm = user.fcm_token
            fcm(leave_issuer_fcm, request.user.get_full_name(),
                leave.id, "approve_compensation")
        except Exception as e:
            print(e)
        if send_email_notification(update_details=update_details):
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def get_own_compensationLeave_detail_monthly(lms_user_id):
    user_detail = {}
    try:
        monthly_leave = []
        lms_user = LmsUser.objects.get(id=lms_user_id)
        user_detail.update({
            'full_name': lms_user.user.get_full_name(),
            'leaves': monthly_leave,
        })

        leaves = get_monthly_compensationLeave_detail_by_id_month(lms_user.id)

        for leave in leaves:
            monthly_leave.append({
                'name': leave.user,
                'days': leave.days,
                'id': leave.id,
                'leave_pending': leave.leave_pending,
                'leave_approved': leave.leave_approved
            })
        user_detail.update({
            'leaves': monthly_leave
        })

        return user_detail
    except (LmsUser.DoesNotExist, Exception) as e:
        print(e)
        return user_detail


def get_monthly_compensationLeave_detail_by_id_month(lms_user_id):
    leave = CompensationLeave.objects.filter(user__id=lms_user_id)
    return leave


def get_user_compensationLeave_detail(lms_user_id, user):
    user_detail = {}
    try:
        monthly_leave = []
        lms_user = LmsUser.objects.get(id=lms_user_id)
        user_detail.update({
            'full_name': lms_user.user.get_full_name(),
            'leaves': monthly_leave,
        })

        if LmsUser.objects.filter(leave_issuer=user):
            leaves = get_monthly_compensationLeave_detail_of_all_user(user)
        else:
            leaves = get_monthly_compensationLeave_detail(lms_user_id)

        for leave in leaves:
            monthly_leave.append({
                'name': leave.user,
                'days': leave.days,
                'id': leave.id,
                'leave_pending': leave.leave_pending,
                'leave_approved': leave.leave_approved
            })
        user_detail.update({
            'leaves': monthly_leave
        })

        return user_detail
    except (LmsUser.DoesNotExist, Exception) as e:
        print(e)
        return user_detail


def get_users_leaveDetailFor_searchEngine(my_leave_approvees, from_date, to_date):
    """
        Parameter
        ---------------------------------------------
        my_leave_approvees: gets logged in user object
        from_date: gets value from user inputstr(
        to_date: gets value from user input

        Loops and Conditions
        ----------------------------------------------
        for loop: gets all leave for requested user from from_date to to_date which is
        has already been approved

        if half day is apllied then 0.5 else 1

        if leave.user.user.get_full_name() in name_list: It checks if the fetched user has
        already been fetched before or not,
            If yes then adds the leaves days in total_days
            otherwise, add to list

        Return
        -------------------------------------------------
        It returns list of user excluding duplicated user

    """
    leave_issuer = LmsUser.objects.filter(leave_issuer=my_leave_approvees)
    name_list = {}
    total_days = 0
    for leave in Leave.objects.order_by("-id").filter(user__in=leave_issuer, from_date__gte=from_date, to_date__lte=to_date, leave_approved=True):
        print(leave)
        leave_multiplier = 1
        if leave.half_day:
            leave_multiplier = 0.5
        total_days = ((leave.to_date - leave.from_date).days +
                      1) * leave_multiplier

        if leave.user.user.get_full_name() in name_list:
            name_list[leave.user.user.get_full_name()] = {
                'id': leave.user.user.id,
                'total_days': name_list[leave.user.user.get_full_name()]['total_days'] + total_days
            }
        else:
            name_list[leave.user.user.get_full_name()] = {
                'id': leave.user.user.id,
                'total_days': total_days
            }

    return name_list


def get_data(leave_of_lmsUser):
    data = []

    for leave in leave_of_lmsUser:
        multiplier = 1
        if leave.half_day:
            multiplier = 0.5

        data.append({
            'from': leave.from_date,
            'to': leave.to_date,
            'half_day': leave.half_day,
            'total_days': ((leave.to_date - leave.from_date).days + 1) * multiplier,
        })

    return data


def check_leave_date(request, leave):
    if leave.from_date >= date.today():
        return True
    else:
        return False


def has_leave(user):
    sick_leave = user.sick_leave
    annual_leave = user.annual_leave

    data = {
        "sick_leave": sick_leave,
        "annual_leave": annual_leave
    }

    return data
