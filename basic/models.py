from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class StudentInfo(models.Model):
    userid = models.ForeignKey(User)
    major = models.CharField(max_length=10)
    graddate = models.DateField()
    progress = models.TextField()
    schedule = models.TextField()


class Instructor(models.Model):
    instructorid = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    rating = models.FloatField()
    email = models.EmailField()

class Course(models.Model):
    courseid = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=10)
    coursecode = models.CharField(max_length=10)
    title = models.CharField(max_length=50)
    instructorid = models.ForeignKey(Instructor)
    req = models.CharField(max_length=100)
    genedflag = models.BooleanField(default=False)
    days = models.CharField(max_length=100)
    coursetime = models.CharField(max_length=100)
    units = models.IntegerField()

class FlightPlan(models.Model):
    flightplanID = models.AutoField(primary_key=True)
    content = models.TextField()
    major = models.CharField(max_length=10)
    majorname = models.CharField(max_length=50)
    graddate = models.DateField()
    def __str__(self):
        return self.major


# STUDENT(StudentId, FirstName, LastName, School, GraduationDate)
# COURSE(CourseId, CourseCode, CourseName, School, InstructorId, GenEdFlag, DualCredit, Mon, Tues, Wed, Thu, Fri, Sat, Sun)
# INSTRUCTOR(InstructorId, FirstName, LastName, CourseId, Rating)
# PROGRESS(ProgressId, StudentId, CourseId, CompletionFlag, OralCommunication, Humanities, Arts, CulturalDiversity1, CulturalDiversity2, SocialSciences)
