from employee import models as employee_models
from support import models as support_models
from services import models as service_models
from datetime import datetime
from hrm import models as hrm_models
from leave_manager import models as leave_models
from lms_user import models as lms_user_model


def get_current_user_branch(user):
    try:
        employee = employee_models.Employee.objects.get(user=user)
        return employee.branch.all()
    except (Exception, employee_models.Employee.DoesNotExist) as e:
        print("Current user branch ", e)
        return support_models.Branches.objects.none()


def get_new_employee_by_branch(branch):
    employee = employee_models.Employee.objects.filter(branch=branch).order_by("-id")[:10]
    return employee


def user_has_multiple_branch(user):
    try:
        employee = employee_models.Employee.objects.get(user=user)
        if len(employee.branch.all()) > 1:
            return True
    except (Exception, employee_models.Employee.DoesNotExist) as e:
        print(" User has multiple branch? ", e)

    return False


def has_hrm_service():
    all_services = service_models.service_requested.objects.first()
    services_ = all_services.services.all()

    for data in services_:
        if data.service_name == "Human Resource Management System" and data.status != "Deactivated":
            return True

    return False


def is_hrm_expired():
    all_services = service_models.service_requested.objects.first()
    services_ = all_services.services.all()
    hr_date = ''

    for data in services_:
        if data.service_name == "Human Resource Management System":
            hr_date = data.expiry_date

    

    delta = hr_date - datetime.now().date()
    return delta.days


def has_hrm_access_to_user(user):   
    try:
        employee = employee_models.Employee.objects.get(user=user)
        user = hrm_models.hr_user.objects.get(employee=employee)
        return user, True
    except (Exception, hrm_models.hr_user.DoesNotExist, employee_models.Employee.DoesNotExist) as e:
        print(e)
        return '', False

def get_all_employee_by_branch(branch):
    emp = employee_models.Employee.objects.filter(branch=branch)
    return emp


def hr_user_type(request):
    try:
        emp = employee_models.Employee.objects.get(user=request.user)
        hr = hrm_models.hr_user.objects.get(employee=emp)
        return hr.hr_type
    except (Exception, employee_models.Employee.DoesNotExist, hrm_models.hr_user.DoesNotExist) as e:
        return ''


def get_employee_by_id(id):
    emp = employee_models.Employee.objects.none()
    try:
        emp = employee_models.Employee.objects.get(id=id)
        return emp, True
    except (Exception, employee_models.Employee.DoesNotExist) as e:
        return emp, False


def get_employee_salary_details(employee):
    salary = employee_models.Salary.objects.filter(employee=employee).order_by("-month")
    return salary


def has_lms_access(user):
    try:
        employee = employee_models.Employee.objects.get(user=user)
        lms = lms_user_model.LmsUser.objects.get(employee=employee)
        return lms, True
    except (Exception, employee_models.Employee.DoesNotExist) as e:
        print(e)
        return '' , False

