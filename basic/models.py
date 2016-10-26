from django.db import models

# Create your models here.

class Student(models.Model):
    studentid = models.AutoField(primary_key=True)
    email = models.CharField(max_length=50, default='user@louisville.edu')
    password = models.CharField(max_length=20, default = 'password')
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    major = models.CharField(max_length=50)
    graduationdate = models.DateField()
    class Meta:
        db_table = 'student'
    def __str__(self):  # __unicode__ on Python 2
        return self.firstname + " " + self.lastname
class Instructor(models.Model):
    instructorid = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    rating = models.FloatField()

class Course(models.Model):
    courseid = models.AutoField(primary_key=True)
    coursecode = models.CharField(max_length=10)
    coursename = models.CharField(max_length=50)
    school = models.CharField(max_length=50)
    instructorid = models.ForeignKey(Instructor)
    genedflag = models.BooleanField(default=False)
    coursetime = models.CharField(max_length=200)

class Progress(models.Model):
    progressid = models.AutoField(primary_key=True)
    studentid = models.ForeignKey(Student)
    courseid = models.ForeignKey(Course)
    completionflag = models.BooleanField(default=False)
    genedlist = models.CharField(max_length=200)

class FlightPlan(models.Model):
    flightplanID = models.AutoField(primary_key=True)
    content = models.TextField()


# STUDENT(StudentId, FirstName, LastName, School, GraduationDate)
# COURSE(CourseId, CourseCode, CourseName, School, InstructorId, GenEdFlag, DualCredit, Mon, Tues, Wed, Thu, Fri, Sat, Sun)
# INSTRUCTOR(InstructorId, FirstName, LastName, CourseId, Rating)
# PROGRESS(ProgressId, StudentId, CourseId, CompletionFlag, OralCommunication, Humanities, Arts, CulturalDiversity1, CulturalDiversity2, SocialSciences)
