from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# This model is for the student info for a user, which is a userid, their major, 
# graduation date, their progress, and their last schedule generated
class StudentInfo(models.Model):
    userid = models.ForeignKey(User)
    major = models.CharField(max_length=10)
    graddate = models.DateField()
    progress = models.TextField()
    schedule = models.TextField()

# This model is for a course, which contains the course id, the subject, course code, the title, the instructor, the pre requisites, 
# whether or not is it a gen ed, the class meeting days, what time the class meets on days, and the credit hours for that class
class Course(models.Model):
    courseid = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=10)
    coursecode = models.CharField(max_length=10)
    title = models.CharField(max_length=50)
    instructor = models.CharField(max_length=100)
    req = models.CharField(max_length=100)
    genedflag = models.BooleanField(default=False)
    days = models.CharField(max_length=100)
    coursetime = models.CharField(max_length=100)
    units = models.IntegerField()

# This class is a representation of what is needed for a flight plan which is the content ie what classes are needed, major,
# major name, graduation date. 
class FlightPlan(models.Model):
    flightplanID = models.AutoField(primary_key=True)
    content = models.TextField()
    major = models.CharField(max_length=10)
    majorname = models.CharField(max_length=50)
    graddate = models.DateField()


# STUDENT(StudentId, FirstName, LastName, School, GraduationDate)
# COURSE(CourseId, CourseCode, CourseName, School, InstructorId, GenEdFlag, DualCredit, Mon, Tues, Wed, Thu, Fri, Sat, Sun)
# INSTRUCTOR(InstructorId, FirstName, LastName, CourseId, Rating)
# PROGRESS(ProgressId, StudentId, CourseId, CompletionFlag, OralCommunication, Humanities, Arts, CulturalDiversity1, CulturalDiversity2, SocialSciences)
