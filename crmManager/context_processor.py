from services import models as service_models
from helper.common import manager as helper_manager


def common(request):
    context = {}
    company_info = service_models.service_requested.objects.first()
    if company_info:
        context.update({
            "company_name": company_info.company_name,
        })

    if request.user.is_authenticated:
        total_branch = helper_manager.user_has_multiple_branch(request.user)

        if total_branch:
            branches = helper_manager.get_current_user_branch(request.user)
            context.update({"total_branch": branches})

    return context
