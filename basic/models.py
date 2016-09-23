from django.db import models

# Create your models here.

class Student(models.Model):
    studentid = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    major = models.CharField(max_length=50)
    graduationdate = models.DateField()
    class Meta:
        db_table = 'student'
    def __str__(self):  # __unicode__ on Python 2
        return self.firstname + " " + self.lastname

# STUDENT(StudentId, FirstName, LastName, School, GraduationDate)
# COURSE(CourseId, CourseCode, CourseName, School, InstructorId, GenEdFlag, DualCredit, Mon, Tues, Wed, Thu, Fri, Sat, Sun)
# INSTRUCTOR(InstructorId, FirstName, LastName, CourseId, Rating)
# PROGRESS(ProgressId, StudentId, CourseId, CompletionFlag, OralCommunication, Humanities, Arts, CulturalDiversity1, CulturalDiversity2, SocialSciences)
