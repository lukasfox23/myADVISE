from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "basic/basic.html")

def about(request):
    return render(request, "basic/about.html")
