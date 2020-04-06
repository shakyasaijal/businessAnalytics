from datetime import datetime
from django.db.models import Q
from leave_manager import models as leave_models
from lms_user import models as lms_user_models
from services import models as services_model
from employee import models as employee_models
from notifications import models as notification_models


def leaves_percentage(lms_user):
    leave_types = leave_models.LeaveType.objects.all()
    data = []
    for data in leave_types:
        leaves_on_leave_type = leave_models.Leave.objects.filter(Q(user=lms_user) & Q(type=data) & ~Q(leave_pending=False, leave_approved=False) & Q(to_date__year=datetime.now().year))
        per =  (len(leaves_on_leave_type)/data.leave_per_year)*100

        diff = 100 - per
        data.append({
            "name": data.type,
            "per_year": data.leave_per_year,
            "taken": len(leaves_on_leave_type),
            "remaining": data.leave_per_year - len(leaves_on_leave_type),
            "percentage_remaining": diff
        })
    return data
