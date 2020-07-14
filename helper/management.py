from employee import models as employee_models

employee_type = (
    ("Ownership", "Ownership"),
    ("Staff", "Staff"),
    ("Staff Head", "Staff Head"),
    ("Cashier", "Cashier"),
    ("Office Head", "Office Head"),
)

def can_crud_holidays(user):
    try:
        emp = employee_models.Employee.objects.get(user=user)
        dep = employee_models.Department.objects.filter(department_head=user)
        user_type = False
        for data in emp.user_type:
            if data == "Ownership" or data == "Office Head":
                user_type = True
        if dep or user_type:
            return True
        return False
    except (Exception, employee_models.Employee.DoesNotExist) as e:
        print(e)
        return False
