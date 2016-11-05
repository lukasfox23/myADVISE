from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from myADVISE.forms import UserForm
#login view request is named login...renamed default django function for clairty
from django.contrib.auth import login as auth_login
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

def create(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            auth_login(request, new_user)
            # redirect, or however you want to get to the main view
            return render(request, "basic/basic.html")
    else:
        form = UserForm()
        return render(request, 'basic/create.html', {'form': form})
