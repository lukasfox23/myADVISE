import json
import time
import copy
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
#import necessary models
from django.contrib.auth.models import User
from basic.models import FlightPlan,StudentInfo,Course
from myADVISE.forms import UserForm
#login view request is named login...renamed default django function for clairty
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from datetime import datetime,timedelta
from django.template import RequestContext
# Create your views here.

@login_required(login_url='login/')
# Param request - request to the main page
# Returns main page
# This function returns the main page of the website if the user is logged in.
def index(request):
    return render(request, "basic/basic.html")

@login_required(login_url='../login/')
# Param request - Request to the progress page
# Returns Progress page
# This function returns the progress page for the current user, it will grab the current user's progress, which is determined by
# by class courses included in a student's flightplan and pass that in to the progress page as the flightplan
# along with the current user, this will happen if the user is logged in.
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
                if(classes['complete'] == True):
                    stillTrue = False
                    for index in range(len(Complete)):
                        if Complete[index] == classes['course']:
                            stillTrue = True
                            break
                    classes['complete'] = stillTrue

        for semester in flightplan['semesters']:
            for classes in semester['classes']:
                for index in range(len(Complete)):
                    if Complete[index] == classes['course']:
                        classes['complete'] = True

        #re-encode the json
        UpdatedFlightPlan = json.dumps(flightplan)
        #Update db for current user
        StudentInfo.objects.filter(userid=current_user.id).update(progress = UpdatedFlightPlan)
    return render(request, "basic/progress.html", {'FlightPlan': flightplan, 'currentUser':current_user})

# Param request - Request to the login page
# Returns login page
# This function will return the Login page for the user to attempt to log in.
def login(request):
    return render(request, "basic/login.html")

# Param request - Request to the create user page
# Returns create user page
# This function will return the create user page, the page will attempt to create the user if the credentials they provide are valid
# if they are not it will return the same page otherwise return them to the main page.
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
                userInfo = StudentInfo(userid=new_user, major=data['major'],credithour = 15, desiredhours = "Don't Care", graddate=datetime.now(), progress=userPlan.content, schedule='none')
                userInfo.save()
            # redirect, or however you want to get to the main view
            return render(request, "basic/basic.html")
    else:
        form = UserForm()
        return render(request, 'basic/create.html', {'form': form})

@login_required(login_url='../login/')
# Param request - Request to the profile page
# Returns profile page
# This function will return the profile page if the user is logged in, this will grab the major, progress, and flightplan of
# the current user to give to the profile page to display and or update. The user can use this page to add preferences to schedule
# generation or change their major, also displays a progress bar for the courses completion
def profile(request):

    current_user, major, progressTotal, flightplan, Schedule, CourseDict = ProgressBar(request)

    # Action from Modals
    if request.method == "POST":
        CreditHours = request.POST.get('CreditHours')
        DesiredHours = request.POST.get('DesiredHours')
        NewMajor = request.POST.get('NewMajor')

        # If the user doesn't want to change their major
        if NewMajor is None:
            # Update Params Modal
            StudentInfo.objects.filter(userid=current_user.id).update(desiredhours=DesiredHours, credithour=CreditHours)
            return render(request, "basic/profile.html", {'currentUser':current_user, 'major':major, 'progressTotal':progressTotal, 'FlightPlan':flightplan, 'Schedule':Schedule, 'CourseDict':CourseDict})
        elif major.major == NewMajor:
            # User tried to update their major without changing their major, do nothing
            return render(request, "basic/profile.html", {'currentUser':current_user, 'major':major, 'progressTotal':progressTotal, 'FlightPlan':flightplan, 'Schedule':Schedule, 'CourseDict':CourseDict})
        else:
            # Update Major
            NewFlightPlanJson = FlightPlan.objects.get(major=NewMajor)
            StudentInfo.objects.filter(userid=current_user.id).update(progress=NewFlightPlanJson.content, major=NewMajor)

            currentUser, major, progressTotal, flightplan = ProgressBar(request)

            return render(request, "basic/profile.html", {'currentUser':current_user, 'major':major, 'progressTotal':progressTotal, 'FlightPlan':flightplan, 'Schedule':Schedule, 'CourseDict':CourseDict})

    return render(request, "basic/profile.html", {'currentUser':current_user, 'major':major, 'progressTotal':progressTotal, 'FlightPlan':flightplan, 'Schedule':Schedule, 'CourseDict':CourseDict})

# Param request - Request to the progress action
# Returns user information related to the user which is the current user, major, progress total, and flightplan of that user
# This function will return everything for the profile page to use, also used
# for the progress bar to display how close the user is to completion
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

    # Grabbing the schedule
    EncodedSchedule = user_list[0].schedule
    DecodedSchedule = json.loads(EncodedSchedule)

    # Get Times/Dates
    CourseName = ''
    CourseDict = {}
    TimeDict = {}

    # Create a coursename, date, time dict from schedule
    for key,value in DecodedSchedule.items():
        Time = value['coursetime'].split(',')
        TempDays = value['days'].split(',')

        # Replace Th with H
        for index in range(len(TempDays)):
            TempDays[index].upper()
            TempDays[index] = TempDays[index].replace("Th", "Z")
            TempDays[index] = TempDays[index].replace("TH", "Z")

        # Finish up dict
        Days = TempDays
        CourseName = value['subject'] + ' ' + value['coursecode']
        TimeDict = dict(zip(Days, Time))
        CourseDict[CourseName] = TimeDict

    return current_user, major, progressTotal, flightplan, DecodedSchedule, CourseDict

@login_required(login_url='../login/')
# Param request - Request to the schedule page
# Returns schedule page
# This function will return the schedule page if the user is logged in. It will grab everything it needs for the user and attempt
# to create a schedule for the next semester of classes for that user based on their progress so far.
def schedule(request):
    current_user = request.user
    #Get user info and preferences
    user_list = StudentInfo.objects.get(userid=current_user.id)
    temp = user_list.progress
    preferredHours = user_list.credithour
    desiredHours = user_list.desiredhours
    flightplan = json.loads(temp)
    classList = []
    genedList = []
    hoursList = []
    #collect courses still needed for graduation
    for semester in flightplan["semesters"]:
        for course in semester["classes"]:
            if(course['complete'] != True):
                classList.append(course)
            if(semester['id'] == "Gen Eds" and course['complete'] != True):
                genedList.append(course)
    #If co-op is next required course, only schedule the co-op. Otherwise ignore all co-ops
    if("CO-OP" in classList[0]['course'] and "SEMINAR" not in classList[0]['course']):
        temp = classList[0]
        classList = []
        classList.append(temp)
        classHours = 2
        #correct amount of hours needed for fulltime
        preferredHours = 0
    else:
        for thisClass in classList:
            if("CO-OP" in thisClass['course'] and "SEMINAR" not in classList[0]['course'] ):
                classList.remove(thisClass)
    semesterCourses=[]
    #retrieve all possible classes for scheduling
    for thisClass in classList:
        classObject = Course.objects.filter(subject = thisClass['subject'], coursecode=thisClass['nbr']).exclude(coursetime = "")
        if(classObject):
            semesterCourses.append(classObject)

    #select final courses
    schedule = []
    timeRanges = [[] for i in range(5)]
    classHours = 0
    scheduleDone = False
    courseScheduled = False

    preferencesExhausted = False

    if(desiredHours != "Don't Care"):
        while(preferencesExhausted == False):
            for courseSet in semesterCourses:
                courseScheduled = False
                finishedSet = False
                while(courseScheduled == False and finishedSet == False):
                    for thisCourse in courseSet:
                        if(classHours + int(thisCourse.units) > preferredHours + 1):
                            scheduleDone = True
                            courseScheduled = True
                            break
                        else:
                            timeRangesT = copy.deepcopy(timeRanges)
                            timeString = thisCourse.coursetime.split(",")
                            meetPref = True
                            for time in timeString:
                                splitTimes = time.split('-')
                                if(desiredHours == 'After Noon'):
                                    if 'am' in splitTimes[0]:
                                        meetPref = False
                                elif(desiredHours == 'Before Noon'):
                                    if 'pm' in splitTimes[0]:
                                        meetPref = False

                            if(meetPref == False):
                                break

                            conflict=checkConflict(timeRangesT, thisCourse)
                            if(conflict == False):
                                timeRanges = timeRangesT
                                schedule.append(thisCourse)
                                classHours = classHours + int(thisCourse.units)
                                courseScheduled = True
                                break
                    finishedSet = True
            preferencesExhausted = True

    while(scheduleDone == False):
        for courseSet in semesterCourses:
            courseScheduled = False
            #loop through variations of courses until one is scheduled
            finishedSet = False
            while(courseScheduled == False and finishedSet == False):
                for thisCourse in courseSet:
                    #Check if the preffered hours are greatly exceeded
                    if((classHours + int(thisCourse.units))> (preferredHours + 1)):
                        scheduleDone = True
                        courseScheduled = True
                        break
                    else:
                        timeRangesT = copy.deepcopy(timeRanges)
                        conflict=checkConflict(timeRangesT, thisCourse)
                        if(conflict == False):
                            timeRanges = timeRangesT
                            schedule.append(thisCourse)
                            classHours = classHours + int(thisCourse.units)
                            courseScheduled = True
                            break
                    finishedSet = True
        scheduleDone = True
    #schedule gened if available
    genedFound = False

    isCoop = False
    if('SEMINAR' not in schedule[0].title):
        if("CO-OP" in schedule[0].title):
            isCoop = True
    if(genedList and isCoop is False):
        courseList = Course.objects.filter(genedflag = True).exclude(coursetime = "")
        while(genedFound == False):
            for gened in genedList:
                if(genedFound == True):
                    break
                for course in courseList:
                    courseName = course.title
                    if("-" in courseName):
                        req = courseName.split("-")
                        if(gened['subject'] == req[1]):
                            timeRangesT = copy.deepcopy(timeRanges)
                            conflict=checkConflict(timeRangesT, course)
                            if(conflict == False):
                                timeRanges = timeRangesT
                                schedule.append(course)
                                genedFound = True
                                courseScheduled = True
                                break
            genedFound = True
    finalSchedule = dict()
    for course in schedule:
        finalSchedule[course.courseid] = dict(subject=course.subject,coursecode=course.coursecode,title=course.title,days=course.days,coursetime=course.coursetime)
    finalSchedule = json.dumps(finalSchedule)
    user_list.schedule = finalSchedule
    user_list.save()
    current_user, major, progressTotal, flightplan, Schedule, CourseDict = ProgressBar(request)
    return render(request, "basic/profile.html", {'currentUser':current_user, 'major':major, 'progressTotal':progressTotal, 'FlightPlan':flightplan, 'Schedule':Schedule, 'CourseDict':CourseDict})

def convert_to_seconds(thisTime):
    afternoonFlag = False
    #adjust for pm if needed
    if(thisTime and thisTime.endswith("pm")):
        afternoonFlag = True
    #cut empty spaces and parsing errors
    if(thisTime[0] == " "):
        thisTime = thisTime[1:6]
        if(thisTime.startswith("12")):
            afternoonFlag = False
    else:
        thisTime = thisTime[0:5]
        if(thisTime.startswith("12")):
            afternoonFlag = False
    x = time.strptime(thisTime,'%H:%M')
    #if pm add extra seconds
    thisTime = timedelta(hours=x.tm_hour,minutes=x.tm_min).total_seconds()
    if(afternoonFlag):
        thisTime = thisTime + 43200
    thisTime
    return thisTime


def time_range_to_seconds(time_str):
	times = time_str.split('-')

	a1 = convert_to_seconds(times[0])
	a2 = convert_to_seconds(times[1])

	return a1, a2

def check_range_intersect(a1, a2, b1, b2):
	if(a1 <= b2) and (a2 >= b1):
		return True;
	return False;

####
# checks if course times overlap
# param timeRanges: stores current time ranges for scheduled courses
# param course: course to be added
# returns bool indicating conflict
def checkConflict(timeRangesT, course):
    days = course.days
    days = days.split(",")
    timeString = course.coursetime.split(",")
    conflict = False
    for i in range(len(days)):
        daysOffered = []
        if('Th' in days[i]):
            daysOffered.append(3)
            days[i] = days[i].replace("Th", "", 1)

        for day in days[i]:
            if day == 'M':
                daysOffered.append(0)
            elif day == 'T':
                daysOffered.append(1)
            elif day == 'W':
                daysOffered.append(2)
            elif day == 'F':
                daysOffered.append(4)

        a1, a2 = time_range_to_seconds(timeString[i])

        for day in daysOffered:
            print day
            for timeRange in timeRangesT[day]:
                b1 = timeRange[0]
                b2 = timeRange[1]
                if(check_range_intersect(a1, a2, b1, b2) == True):
                    conflict = True

        if(conflict == False):
            timeRange = [a1, a2]
            for day in daysOffered:
                timeRangesT[day].append(timeRange)
        else:
            break

    return conflict
