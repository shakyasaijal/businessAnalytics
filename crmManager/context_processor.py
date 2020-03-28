from services import models as service_models
from helper.common import manager as helper_manager
from employee import models as employee_models


def common(request):
    context = {}
    company_info = service_models.service_requested.objects.first()
    if company_info:
        context.update({
            "company_name": company_info.company_name,
        })

    if request.user.is_authenticated:
        total_branch = helper_manager.user_has_multiple_branch(request.user)
        employee = employee_models.Employee.objects.none()
        try:
            employee = employee_models.Employee.objects.get(user=request.user)
        except (Exception, employee_models.Employee.DoesNotExist) as e:
            pass

        if total_branch:
            branches = helper_manager.get_current_user_branch(request.user)
            context.update({"total_branch": branches})

        if employee:
            context.update({"context_employee": employee})
    return context
