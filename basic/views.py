import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
#import necessary models
from django.contrib.auth.models import User
from basic.models import FlightPlan,StudentInfo,Course
from myADVISE.forms import UserForm
#login view request is named login...renamed default django function for clairty
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from datetime import datetime
from django.template import RequestContext
# Create your views here.

@login_required(login_url='login/')
def index(request):
    return render(request, "basic/basic.html")

@login_required(login_url='../login/')
def progress(request):
    current_user = request.user
    user_list = StudentInfo.objects.filter(userid=current_user.id)[:1]
    temp = user_list[0].progress
    #decode the json
    flightplan = json.loads(temp)

    #Get coursenames of checks, iterate through flightplan, mark as complete when match
    if request.method == "POST":
        Complete = request.POST.getlist('check')
        for semester in flightplan['semesters']:
            for classes in semester['classes']:
                for index in range(len(Complete)):
                    if Complete[index] == classes['course']:
                        classes['complete'] = True
                        #print(classes['course'])
                        #print(classes['complete'])

        #re-encode the json
        UpdatedFlightPlan = json.dumps(flightplan)
        #Update db for current user
        StudentInfo.objects.filter(userid=current_user.id).update(progress = UpdatedFlightPlan)

        return render(request, "basic/basic.html")

    return render(request, "basic/progress.html", {'FlightPlan': flightplan, 'currentUser':current_user})

def login(request):
    return render(request, "basic/login.html")

def create(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            new_user = User.objects.create_user(username=data['username'], password=data['password'], email=data['email'])
            new_user = authenticate(username=data['username'], password=data['password'])
            if new_user:
                auth_login(request, new_user)
                userPlan = FlightPlan.objects.get(major=data['major'])
                userInfo = StudentInfo(userid=new_user, major=data['major'], graddate=datetime.now(), progress=userPlan.content, schedule='none')
                userInfo.save()
            # redirect, or however you want to get to the main view
            return render(request, "basic/basic.html")
    else:
        form = UserForm()
        return render(request, 'basic/create.html', {'form': form})

@login_required(login_url='../login/')
def profile(request):

    current_user, major, progressTotal, flightplan = ProgressBar(request)

    # Action from Modals
    if request.method == "POST":
        CreditHours = request.POST.get('CreditHours')
        DesiredHours = request.POST.getlist('DesiredHours')
        NewMajor = request.POST.get('NewMajor')

        # If the user doesn't want to change their major
        if NewMajor is None:
            # Update Params Modal
            return render(request, "basic/profile.html", {'currentUser':current_user, 'major':major, 'progressTotal':progressTotal, 'FlightPlan':flightplan})
        elif major.major == NewMajor:
            # User tried to update their major without changing their major, do nothing
            return render(request, "basic/profile.html", {'currentUser':current_user, 'major':major, 'progressTotal':progressTotal, 'FlightPlan':flightplan})
        else:
            # Update Major
            NewFlightPlanJson = FlightPlan.objects.get(major=NewMajor)
            StudentInfo.objects.filter(userid=current_user.id).update(progress=NewFlightPlanJson.content, major=NewMajor)

            currentUser, major, progressTotal, flightplan = ProgressBar(request)

            return render(request, "basic/profile.html", {'currentUser':current_user, 'major':major, 'progressTotal':progressTotal, 'FlightPlan':flightplan})

    return render(request, "basic/profile.html", {'currentUser':current_user, 'major':major, 'progressTotal':progressTotal, 'FlightPlan':flightplan})

def ProgressBar(request):
    current_user = request.user
    major = StudentInfo.objects.get(userid=current_user.id)
    user_list = StudentInfo.objects.filter(userid=current_user.id)[:1]
    temp = user_list[0].progress
    flightplan = json.loads(temp)
    completeCount = 0.0
    totalCount = 0.0
    for semester in flightplan["semesters"]:
        for course in semester["classes"]:
            totalCount = totalCount + 1
            if(course["complete"] == True):
                completeCount = completeCount + 1
    progressTotal = 0.0
    progressTotal = float(completeCount/totalCount) * 100
    progressTotal = round(progressTotal,2)

    return current_user, major, progressTotal, flightplan

@login_required(login_url='../login/')
def schedule(request):
    current_user = request.user
    major = StudentInfo.objects.get(userid=current_user.id)
    user_list = StudentInfo.objects.filter(userid=current_user.id)[:1]
    temp = user_list[0].progress
    flightplan = json.loads(temp)
    classList = []
    classHours = 0
    scheduleDone = False
    while(scheduleDone != True):
        for semester in flightplan["semesters"]:
            for course in semester["classes"]:
                if(course['complete'] != True):
                    if(classHours + int(course['cr']) > 18):
                        scheduleDone = True
                        break
                    else:
                        classHours = classHours + int(course['cr'])
                        classList.append(course)
    #If co-op is next required course, only schedule the co-op
    if("Co-op" in classList[0]['course']):
        temp = classList[0]
        classList = []
        classHours = temp['cr']
        classList.append(temp)
        classHours = 2
    semesterCourses=[]
    for thisClass in classList:
        semesterCourses.append(Course.objects.filter(subject = thisClass['subject'], coursecode=thisClass['nbr']))
    return render(request, "basic/schedule.html", {'flightplan': classList, 'hours' : classHours})
