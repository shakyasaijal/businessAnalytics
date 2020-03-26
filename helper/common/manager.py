from employee import models as employee_models
from support import models as support_models


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
