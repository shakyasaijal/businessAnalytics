from services import models as service_models


def common(request):
    context = {}
    company_info = service_models.service_requested.objects.first()
    if company_info:
        context.update({
            "company_name": company_info.company_name,
            ""
        })

    return context
