def login_field_error_validate(request):
    has_data = 0
    err = []

    for data in request.POST.items():
        for d in data:
            if d == "username":
                has_data += 1

            if d == "password":
                has_data += 1

    if has_data != 2:
        err.append("Form error.")
        return err

    if not request.POST['username'] or not request.POST['password']:
        err.append('All fields are required.')

    return err