from lms_user.models import LmsUser
from employee import models as employee_models


def is_leave_issuer(user):
    hod = LmsUser.objects.filter(department__head_of_department=user).exists()
    leave_issuer = LmsUser.objects.filter(leave_issuer=user).exists()
    if hod or leave_issuer:
        return True
    else:
        return False


def get_employee_leave_issuer(user):
    try:
        emp = employee_models.Employee.objects.get(user=user)
        lms_user = LmsUser.objects.get(employee = emp)
        if lms_user.leave_issuer:

            return lms_user.leave_issuer, True
        
        return emp.staff_head, True

    except (Exception, employee_models.Employee.DoesNotExist, LmsUser.DoesNotExist) as e:
        print('leave_manager>common>check_leave_admin>25 line ', e)
        return '', False


