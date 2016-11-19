import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
#import necessary models
from django.contrib.auth.models import User
from basic.models import FlightPlan
from basic.models import StudentInfo
from myADVISE.forms import UserForm
#login view request is named login...renamed default django function for clairty
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
# Create your views here.
@login_required(login_url='login/')
def index(request):
    return render(request, "basic/basic.html")

@login_required(login_url='../login/')
def about(request):
    current_user = request.user
    major = StudentInfo.objects.get(userid=current_user.id)
    user_list = FlightPlan.objects.filter(major__contains=major.major)[:1]
    temp = user_list[0].content
    flightplan = json.loads(temp)
    return render(request, "basic/about.html", {'FlightPlan': flightplan, 'currentUser':current_user})

def login(request):
    return render(request, "basic/login.html")

def create(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            new_user = authenticate(username=new_user.username, password=new_user.password)
            if new_user:
                auth_login(request, new_user)
            # redirect, or however you want to get to the main view
            return render(request, "basic/basic.html")
    else:
        form = UserForm()
        return render(request, 'basic/create.html', {'form': form})

@login_required(login_url='../login/')
def profile(request):
    current_user = request.user
    major = StudentInfo.objects.get(userid=current_user.id)
    return render(request, "basic/profile.html", {'currentUser':current_user, 'major':major})
