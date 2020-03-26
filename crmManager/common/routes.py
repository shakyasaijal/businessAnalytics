from django.urls import reverse_lazy

all_navigation_routes = [
    {
        'title': 'list inquiry',
        'url': reverse_lazy('list-inquiry'),
        'manager': True,
        'staff':True,
        'volunteer':False,
        'specialStaff':True,
        'active': False,
        'icon': 'pe-7s-news-paper'
    },
    {
        'title': 'create inquiry',
        'url': reverse_lazy('create-inquiry'),
        'manager': True,
        'staff':True,
        'volunteer':True,
        'specialStaff':True,
        'active': False,
        'icon': 'pe-7s-news-paper'
    },
    {
        'title': 'search bahini',
        'url': reverse_lazy('search_view'),
        'manager': False,
        'staff':False,
        'specialStaff':True,
        'volunteer':False,
        'active': False,
        'icon': 'pe-7s-user'
    },
    {
        'title': 'list bahini',
        'url': reverse_lazy('list-bahini'),
        'manager': True,
        'staff':True,
        'volunteer':True,
        'specialStaff':True,
        'active': False,
        'icon': 'pe-7s-user'
    },
    {
        'title': 'list meeting',
        'url': reverse_lazy('list-meeting'),
        'manager': True,
        'volunteer':False,
        'staff':True,
        'specialStaff':True,
        'active': False,
        'icon': 'pe-7s-ribbon'
    },
    {
        'title': 'list employement record',
        'url': reverse_lazy('list-employement'),
        'manager': False,
        'volunteer':False,
        'staff':True,
        'specialStaff':True,
        'active': False,
        'icon': 'pe-7s-note2'
    },
    {
        'title': 'bahini review',
        'url': reverse_lazy('bahini-review'),
        'manager': True,
        'volunteer':True,
        'staff':False,
        'specialStaff':True,
        'active': False,
        'icon': 'pe-7s-note'
    },
    {
        'title': 'payment records',
        'url': reverse_lazy('payment-record'),
        'manager': True,
        'volunteer':False,
        'staff':True,
        'specialStaff':True,
        'active': False,
        'icon': 'pe-7s-chat'
    },
    {
        'title': 'payment follow up',
        'url': reverse_lazy('payment-follow-up'),
        'manager': False,
        'volunteer':False,
        'staff':False,
        'specialStaff':False,
        'active': False,
        'icon': 'pe-7s-piggy'
    },
    {
        'title': 'list employer',
        'url': reverse_lazy('list-employer'),
        'manager': True,
        'staff':True,
        'specialStaff':False,
        'volunteer':False,
        'active': False,
        'icon': 'pe-7s-user'
    },
    {
        'title': 'track data',
        'url': reverse_lazy('track-data'),
        'manager': True,
        'staff':False,
        'specialStaff':False,
        'volunteer':False,
        'active': False,
        'icon': 'pe-7s-usb'
    },
    {
        'title': 'time based report',
        'url': reverse_lazy('time-based-report'),
        'manager': True,
        'staff':False,
        'specialStaff':False,
        'volunteer':False,
        'active': False,
        'icon': 'pe-7s-print'
    },
    {
        'title': 'company details',
        'url': reverse_lazy('company-details'),
        'manager': True,
        'volunteer':False,
        'staff':False,
        'specialStaff':False,
        'active': False,
        'icon': 'pe-7s-id'
    },
    {
        'title': 'validate bahini records',
        'url': reverse_lazy('validate-bahini'),
        'manager': False,
        'volunteer':False,
        'staff':True,
        'specialStaff':True,
        'active': False,
        'icon': 'pe-7s-ribbon'
    },
    {
        'title': 'webapp assets',
        'url': reverse_lazy('webapp-assets'),
        'manager': True,
        'volunteer':True,
        'staff':True,
        'specialStaff':True,
        'active': False,
        'icon': 'pe-7s-helm'
    },
    {
        'title': 'list users',
        'url': reverse_lazy('list-users'),
        'manager': True,
        'volunteer':False,
        'staff':False,
        'specialStaff':False,
        'active': False,
        'icon': 'pe-7s-helm'
    }   
]


staff_navigation_routes = [route for route in all_navigation_routes if route['staff']]
specialStaff_navigation_routes = [route for route in all_navigation_routes if route['specialStaff']]
volunteer_navigation_routes = [route for route in all_navigation_routes if route['volunteer']]
manager_navigation_routes = [route for route in all_navigation_routes if route['manager'] or route['staff']]

def get_routes(user):
    if is_special_staff(user):
        return specialStaff_navigation_routes
    if is_manager(user):
        return manager_navigation_routes
    if is_staff(user):
        return staff_navigation_routes
    if is_volunteer(user):
        return volunteer_navigation_routes
    if is_admin(user):
        return all_navigation_routes


def get_formatted_routes(routes, active_page):
    formatted_routes = []
    for route in routes:
        route['active'] = False
        if route['title'] == active_page:
            route['active'] = True
        formatted_routes.append(route)
    return formatted_routes
    
