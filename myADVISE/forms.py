from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from basic.models import FlightPlan
from django import forms

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password', 'type':'password'}))

class UserForm(forms.Form):
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    email = forms.CharField(label="Email", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'email'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password', 'type':'password'}))
    options = (
        ('BE', 'Bio-engineering'),
        ('CHE', 'Chemical Engineering'),
        ('CE', 'Civil Engineering'),
        ('CECS', 'Computer Science and Engineering'),
        ('ECE', 'Electrical and Computer Engineering'),
        ('IE', 'Industrial Engineering'),
        ('ME', 'Mechanical Engineering'),
    )
    major = forms.ChoiceField(label="Major", choices=options, widget=forms.Select(attrs={'name':'major'}))
