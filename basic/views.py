from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from basic.models import Student
# Create your views here.
@login_required(login_url='login/')
def index(request):
    return render(request, "basic/basic.html")

@login_required(login_url='../login/')
def about(request):
    user_list = User.objects.all()[:50]
    return render(request, "basic/about.html", {'users': user_list})

def login(request):
    return render(request, "basic/login.html")
