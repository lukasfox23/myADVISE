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
                userInfo = StudentInfo(userid=new_user, major=data['major'],credithour = 15, graddate=datetime.now(), progress=userPlan.content, schedule='none')
                userInfo.save()
            # redirect, or however you want to get to the main view
            return render(request, "basic/basic.html")
    else:
        form = UserForm()
        return render(request, 'basic/create.html', {'form': form})

@login_required(login_url='../login/')
def profile(request):
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
    return render(request, "basic/profile.html", {'currentUser':current_user, 'major':major, 'progressTotal':progressTotal})

@login_required(login_url='../login/')
def schedule(request):
    current_user = request.user
    #Get user info and preferences
    user_list = StudentInfo.objects.filter(userid=current_user.id)[:1]
    temp = user_list[0].progress
    preferredHours = user_list[0].credithour
    flightplan = json.loads(temp)
    classList = []
    genedList = []
    #collect courses still needed for graduation
    for semester in flightplan["semesters"]:
        for course in semester["classes"]:
            if(course['complete'] != True):
                classList.append(course)
            if(semester['id'] == "Gen Eds"):
                genedList.append(course)
    #If co-op is next required course, only schedule the co-op. Otherwise ignore all co-ops
    if("Co-op" in classList[0]['course']):
        temp = classList[0]
        classList = []
        classList.append(temp)
        classHours = 2
        #correct amount of hours needed for fulltime
        preferredHours = 0
    else:
        for thisClass in classList:
            if("Co-op" in thisClass['course']):
                classList.remove(thisClass)
    semesterCourses=[]
    #retrieve all possible classes for scheduling
    for thisClass in classList:
        classObject = Course.objects.filter(subject = thisClass['subject'], coursecode=thisClass['nbr'])
        if(classObject):
            semesterCourses.append(classObject)
    #select final courses
    schedule = []
    classHours = 0
    scheduleDone = False
    courseScheduled = False
    while(scheduleDone == False):
        for courseSet in semesterCourses:
            courseScheduled = False
            #loop through variations of courses until one is scheduled
            while(courseScheduled == False):
                for thisCourse in courseSet:
                    #Check if the preffered hours are greatly exceeded
                    if(classHours + int(thisCourse.units) > preferredHours + 1):
                        scheduleDone = True
                        courseScheduled = True
                        break
                    else:
                        schedule.append(thisCourse)
                        classHours = classHours + int(thisCourse.units)
                        courseScheduled = True
                        break
    #schedule gened if available
    genedFound = False
    if(genedList and "CO-OP" not in schedule[0].title):
        schedule.pop()
        courseList = Course.objects.filter(genedflag = True)
        while(genedFound == False):
            for gened in genedList:
                if(genedFound == True):
                    break
                for course in courseList:
                    courseName = course.title
                    if("-" in courseName):
                        req = courseName.split("-")
                        if(gened['subject'] == req[1]):
                            schedule.append(course)
                            genedFound = True
                            break
    return render(request, "basic/schedule.html", {'coursesToSchedule': semesterCourses, 'hours' : classHours, 'neededCourses':classList, 'flightplan':flightplan, 'schedule':schedule})
