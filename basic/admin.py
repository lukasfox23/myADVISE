from django.contrib import admin
from basic.models import Student
from basic.models import Instructor
from basic.models import Course
from basic.models import Progress

# Register your models here.
admin.site.register(Student)
admin.site.register(Instructor)
admin.site.register(Course)
admin.site.register(Progress)
