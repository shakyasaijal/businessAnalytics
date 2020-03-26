from lms_user.models import LmsUser
from employee import models as employee_models
from datetime import datetime, timedelta
from django.db.models import Q
from calendar import monthrange

def get_lms_users():
    users = []
    for lms_user in LmsUser.objects.all():
        try:
            image_url = lms_user.image.url.split('/static/')[1]
        except Exception as e:
            print(e)
            image_url = 'lms_user/images/photograph.png'
        users.append({
            'id':lms_user.user.id,
            'full_name': lms_user.user.get_full_name(),
            'username': lms_user.user.username,
            'phone_number': lms_user.phone_number,
            'email': lms_user.user.email,
            'department': lms_user.department.department,
            'leave_issuer': lms_user.leave_issuer.get_full_name(),
            'leave_issuer_id':lms_user.leave_issuer.id,
            'date_of_birth': str(lms_user.date_of_birth),
            'joined_date': str(lms_user.joined_date),
            'image': image_url
        })
    return users


def get_birthday_today(branch):
    today = datetime.today()
    upcoming_bday_users = []
    date_after_5_days = today+timedelta(6)
    month = []
    day = []
    for date in range(0,5):
        day.append((today+timedelta(date)).day)
        month.append((today+timedelta(date)).month)

    for user in employee_models.Employee.objects.filter(Q(date_of_birth__month__lte=date_after_5_days.month) and Q(date_of_birth__month__gte=today.month), Q(date_of_birth__day__lte=date_after_5_days.day) and Q(date_of_birth__day__gte=today.day) and Q(branch=branch)).order_by("date_of_birth"):
        try:
            image_url = user.picture.url
        except Exception as e:
            print(e)
            image_url = 'https://picsum.photos/200/200'
        for date in range(0,5):
            if user.date_of_birth.month == month[date] and user.date_of_birth.day == day[date]:
                upcoming_bday_users.append({
                    'full_name': user.user.get_full_name(),
                    'dob':user.date_of_birth,
                    'image': image_url,
                    'remaining': date
                    })
    all_data = {
        'upcoming':upcoming_bday_users
        }
    return all_data
