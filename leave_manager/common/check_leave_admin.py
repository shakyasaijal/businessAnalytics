from lms_user.models import LmsUser
from employee import models as employee_models


def is_staff_head(emp):
    emp = employee_models.Employee.objects.filter(staff_head=emp).exists()
    if emp:
        return True
    return False


def is_department_head(user):
    try:
        dep = employee_models.Department.objects.filter(department_head=user)
        return True
    except (Exception, employee_models.Department.DoesNotExist) as e:
        return False


def is_leave_issuer(user):
    try:
        emp = employee_models.Employee.objects.get(user=user)
        issuer = LmsUser.objects.filter(leave_issuer=emp).exists()
        if issuer:
            return True
        return False
    except (Exception, employee_models.Employee.DoesNotExist) as e:
        return False


def get_employee_leave_issuer(user):
    try:
        emp = employee_models.Employee.objects.get(user=user)
        lms_user = LmsUser.objects.get(employee = emp)
        if lms_user.leave_issuer:
            return lms_user.leave_issuer, True
        
        return '', False
    except (Exception, employee_models.Employee.DoesNotExist, LmsUser.DoesNotExist) as e:
        print('leave_manager>common>check_leave_admin>25 line ', e)
        return '', False


