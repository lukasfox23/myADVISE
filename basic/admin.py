from django.contrib import admin
from basic.models import Instructor
from basic.models import Course
from basic.models import FlightPlan
from basic.models import StudentInfo

# Register your models here.
admin.site.register(Instructor)
admin.site.register(Course)
admin.site.register(StudentInfo)
admin.site.register(FlightPlan)
