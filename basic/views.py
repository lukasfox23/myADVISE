from django.shortcuts import render
from basic.models import Student
# Create your views here.
def index(request):
    return render(request, "basic/basic.html")

def about(request):
    user_list = Student.objects.all()[:50]
    return render(request, "basic/about.html", {'users': user_list})

def contact(request):
    return render(request, "basic/contact.html")
