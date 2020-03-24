from django.shortcuts import render

# Create your views here.
def crm_index(request):
    return render(request, "crmManager/index.html")