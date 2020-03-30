from datetime import datetime,timedelta
from django.contrib.auth.models import User
from pprint import pprint
from django.db.models import Q
import re
from django.contrib import messages
from leave_manager import models as leave_models
from lms_user import models as lms_user_models
from employee import models as employee_models



def register_validation(request):
    has_POST = 0
    for d in request.POST:
        if d == "first_name":
            has_POST += 1
        if d == "last_name":  
            has_POST += 1
        if d == "username":  
            has_POST += 1
        if d == "email":  
            has_POST += 1
        if d == "department":  
            has_POST += 1
        if d == "date_of_birth":  
            has_POST += 1
        if d == "joined_date":  
            has_POST += 1
        if d == "password":  
            has_POST += 1
    if has_POST < 8:
        return  messages.success(request, 'Invalid Form Data', extra_tags='0') ,True
    pattern = '^[A-Za-z.\s]+$'
    email = '^[a-zA-Z0-9_.+-]*@[a-zA-Z0-9-]*\.[a-zA-Z0-9-.]+$'
    if not re.match(pattern, request.POST['first_name']) or not re.match(pattern, request.POST['last_name']):
        return messages.success(request,'First and Last name should not contain special characters', extra_tags='0') ,True  
    if len(request.POST['first_name'])<2 or len(request.POST['first_name'])>50 or len(request.POST['last_name'])<2 or len(request.POST['last_name'])>50:
        return messages.success(request,'First and Last name should not be less than 2 and greater than 50', extra_tags='0') ,True    
    if not re.match(email, request.POST['email']):
        return messages.success(request,'Invalid Email', extra_tags='0') ,True    
    try:
        existing_user = User.objects.get(email=request.POST['email'])
        return messages.success(request, 'Could not register to LMS. Email Already exists', extra_tags='0') ,True 
    except (User.DoesNotExist, Exception)  as e:
        print(e)
    try:
        phone = lms_user_models.LmsUser.objects.get(phone_number=request.POST['phone_number'])
        return messages.success(request, 'Could not register to LMS. Phone number Already exists', extra_tags='0') ,True    
    except (lms_user_models.LmsUser.DoesNotExist, Exception) as e:   
        print(e)  
    if not len(request.POST['phone_number']) == 10:
       return messages.success(request, 'Invalid Phone Number.Phone number should be 10 digits', extra_tags='0') ,True  
    if request.POST['date_of_birth'] > str(datetime.today()).split(' ')[0] or request.POST['date_of_birth'] < str(datetime.today() - timedelta(days=365*65)):
        return messages.success(request, 'Invalid Date of Birth', extra_tags='0') ,True
    if request.POST['joined_date'] > str(datetime.today()).split(' ')[0]:
        return messages.success(request,'Invalid Joined Date', extra_tags='0') ,True
    if len(request.POST['username']) >30  or len(request.POST['username']) < 5:
        return messages.success(request, 'Invalid Username', extra_tags='0') ,True  
    try:
        username = User.objects.get(username=request.POST['username'])
        return messages.success(request, 'Could not register to LMS. Username Already exists', extra_tags='0') ,True
    except (lms_user_models.LmsUser.DoesNotExist, Exception) as e:   
        print(e)  
    try:
        email = lms_user_models.LmsUser.objects.get(phone_number=request.POST['email'])
        return messages.success(request, 'Could not register to LMS. Email Already exists', extra_tags='0') ,True
    except (lms_user_models.LmsUser.DoesNotExist, Exception) as e:   
        print(e)  
    return False


def leave_validation(request):
    has_POST = 0
    try:
        leave_type = request.POST['leave_type']
        print(leave_type)
    except Exception as e:
        print(e)
        return  messages.error(request, 'Invalid Form Data') ,True

    for d in request.POST:
        if d == "from_date":
            has_POST += 1
        if d == "to_date":  
            has_POST += 1
        if d == "leave_type":  
            has_POST += 1
        if d == "leave_reason":  
            has_POST += 1
        if d == "half_leave":  
            has_POST += 1
    if has_POST <4:
        return  messages.error(request, 'Invalid Form Data') ,True

    if request.POST['from_date'] < str(datetime.today()).split(' ')[0] or request.POST['to_date'] < str(datetime.today()).split(' ')[0]:
        return messages.error(request, 'Invalid Date') ,True
    if request.POST['from_date'] > request.POST['to_date']:
        return messages.error(request, 'To Date is before From Date') ,True
    return False


def has_leave_on_particular_date(lms_user, date, date1):
    leaves = leave_models.Leave.objects.filter(Q(from_date__month=date.month, from_date__year=date.year) | Q(to_date__month=date.month, to_date__year=date.year)).order_by('id').distinct()

    if leaves:
        data_ = None
        from_data = datetime
        days_ = []
        days_2 = []
        for data in leaves:
            delta = data.to_date - data.from_date
            status = False
            for i in range(delta.days + 1):
                current = data.from_date + timedelta(days=i)
                if current == date or current == date1:
                    status = True
                else:
                    status = False
                days_2.append(current)
                days_.append({
                    "found":current,
                    "status": status
                })
            if date in days_2:
                leave_status = "Pending"
                if data.leave_approved:
                    leave_status = "Approved"

                if not data.leave_approved and not data.leave_pending:
                    leave_status = "Rejected"

                send = {
                    "data": data,
                    "list": days_,
                    "leave_status": leave_status,
                    "reject_reason": data.reject_reason   
                    }
                
                return send, True
            break
            days_ = []
    return leaves, False


def able_to_apply_leave(request):
    from_date = datetime.strptime(request.POST['from_date'], "%Y-%m-%d")
    to_date = datetime.strptime(request.POST['to_date'], "%Y-%m-%d")

    employee = employee_models.Employee.objects.get(user=request.user)
    lms = lms_user_models.LmsUser.objects.get(employee=employee)
    from_date_ = has_leave_on_particular_date(lms, from_date.date(), to_date.date())
    
    if from_date_[1]:
        a = [{
            "from_date": from_date,
            "data": from_date_[0],
            "to_date": to_date
        }]
        return a[0], False
    
    to_date_ = has_leave_on_particular_date(lms, to_date.date(), from_date.date())

    if to_date_[1]:
        a = [{
            "from_date": from_date,
            "data": to_date_[0],
            "to_date": to_date
        }]
        return a[0], False

    
    return '',True


def compensation_validtion(request,context):
    has_POST = 0
    for d in request.POST:
        if d == "days":
            has_POST += 1
        if d == "leave_reason":  
            has_POST += 1
    if has_POST <2:
        return  messages.success(request, 'Invalid Form Data', extra_tags='0') ,True
    if int(request.POST['days']) > 100 or int(request.POST['days']) <= 0:
        return messages.success(request, 'Invalid Number of days', extra_tags='0') ,True
    return False
