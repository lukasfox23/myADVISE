from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from views import index, login, create, profile, ProgressBar
from myADVISE.forms import LoginForm, UserForm
from models import FlightPlan, StudentInfo
from datetime import datetime
import json
# Create your tests here.

class HomePageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user('temporary', 'temporary@louisivlle.edu', 'temporary')

    def test_root_direct_to_basic_view(self):
        found = resolve('/')
        self.assertEqual(found.func, index)

    def test_redirect_to_login(self):
        response = self.client.get('/', follow=False)
        self.assertEquals(302, response.status_code)
        response = self.client.get('/', follow=True)
        self.assertIn('<p>Login</p>', response.content)

    def test_basic_view_access_after_login(self):
        request = self.factory.get('/')
        request.user = self.user
        response = index(request)
        self.assertEquals(200, response.status_code)
        self.assertIn('<p>Optimize your schedule making process!</p>', response.content)


class LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user('temporary', 'temporary@louisivlle.edu', 'temporary')
        self.user = User.objects.create_user('DROP SCHEMA public CASCADE', 'temporary1@louisivlle.edu', 'temp')

    def test_login_view(self):
        request = self.factory.get('/')
        response = login(request)
        self.assertEquals(200, response.status_code)
        self.assertIn('login-submit', response.content)

    def test_login_form_correct(self):
        form_data = {'username': 'temporary', 'password': 'temporary'}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_login_form_incorrect_username(self):
        form_data = {'username': 'temporary1', 'password': 'temporary'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEquals([u'Please enter a correct username and password. Note that both fields may be case-sensitive.'],form.errors['__all__'])

    def test_login_form_incorrect_password(self):
        form_data = {'username': 'temporary', 'password': 'temporary1'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEquals([u'Please enter a correct username and password. Note that both fields may be case-sensitive.'],form.errors['__all__'])

    def test_login_form_username_not_entered(self):
        form_data = {'username': '', 'password': 'temporary'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEquals({'username': [u'This field is required.']},form.errors)

    def test_login_form_password_not_entered(self):
        form_data = {'username': 'temporary', 'password': ''}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEquals({'password': [u'This field is required.']},form.errors)

    def test_login_form_sanitation(self):
        form_data = {'username': 'DROP SCHEMA public CASCADE', 'password': 'temp'}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())
        form_data = {'username': 'temporary', 'password': 'temporary'}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())
        form_data = {'username': ' temporary ', 'password': ' temporary '}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_login_authenticate(self):
        user = authenticate(username='temporary', password='temporary')

class CreateTests(TestCase):
    fixtures = ['myADVISE.json']

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_create_view(self):
        request = self.factory.get('/')
        response = create(request)
        self.assertEquals(200, response.status_code)
        self.assertIn('<p>Create Account</p>', response.content)

    def test_create_form_correct(self):
        form_data = {'username': 'temporary', 'email': 'temporary@louisville.edu', 'password': 'temporary', 'major': 'BE'}
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_create_form_username_not_entered(self):
        form_data = {'username': '', 'email': 'temporary@louisville.edu', 'password': 'temporary', 'major': 'BE'}
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEquals({'username': [u'This field is required.']},form.errors)

    def test_create_form_email_not_entered(self):
        form_data = {'username': 'temporary', 'email': '', 'password': 'temporary', 'major': 'BE'}
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEquals({'email': [u'This field is required.']},form.errors)

    def test_create_form_password_not_entered(self):
        form_data = {'username': 'temporary', 'email': 'temporary@louisville.edu', 'password': '', 'major': 'BE'}
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEquals({'password': [u'This field is required.']},form.errors)

    def test_create_form_major_not_entered(self):
        form_data = {'username': 'temporary', 'email': 'temporary@louisville.edu', 'password': 'temporary', 'major': ''}
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEquals({'major': [u'This field is required.']},form.errors)

    def test_create_user_post(self):
        response = self.client.post('/create/', {'username': 'temporary', 'email': 'temporary@louisville.edu', 'password': 'temporary', 'major': 'BE'})
        user = User.objects.get(username='temporary')
        self.assertEqual(user.username, 'temporary')
        self.assertEqual(user.email, 'temporary@louisville.edu')
        user = authenticate(username='temporary', password='temporary')
        userFlightPlan = StudentInfo.objects.get(userid = user)
        userPlan = FlightPlan.objects.filter(major='BE')[:1]
        self.assertEqual(userFlightPlan.major, 'BE')
        self.assertIn('Intro BioE (Spring)', userFlightPlan.progress)
        self.assertEqual(userFlightPlan.schedule, 'none')
        self.assertEquals(200, response.status_code)
        self.assertIn('<p>Optimize your schedule making process!</p>', response.content)

class ProfileTests(TestCase):
    fixtures = ['myADVISE.json']

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_profile_view(self):
        request = self.factory.get('/')
        request.user = authenticate(username='blakrtest', password='blakrtest')
        response = profile(request)
        self.assertEqual(200, response.status_code)
        self.assertIn('<h2>Current Schedule</h2>', response.content)

    def test_redirect_to_login_when_not_logged_in_profile(self):
        response = self.client.get('/profile', follow=False)
        self.assertEquals(301, response.status_code)
        response = self.client.get('/profile', follow=True)
        self.assertIn('<p>Login</p>', response.content)

    def test_progress_bar_displays(self):
        request = self.factory.get('/')
        request.user = authenticate(username='blakrtest', password='blakrtest')
        response = profile(request)
        self.assertEqual(200, response.status_code)
        self.assertIn('<div class="progress-bar progress-bar-danger"', response.content)

    def test_progress_bar_correct(self):
        request = self.factory.get('/')
        request.user = authenticate(username='blakrtest', password='blakrtest')
        current_user, student, progressTotal, flightplan = ProgressBar(request)
        testStudent = StudentInfo.objects.get(userid = request.user)
        testJson = json.loads(testStudent.progress)
        self.assertEqual(current_user, request.user)
        self.assertEqual(student, testStudent)
        self.assertEqual(progressTotal, 15.09)
        self.assertEqual(flightplan, testJson)

    def test_user_info_display(self):
        request = self.factory.get('/')
        request.user = authenticate(username='blakrtest', password='blakrtest')
        response = profile(request)
        self.assertIn('<h2>blakrtest</h2>', response.content)
        self.assertIn('<h4>Major: BE</h4>', response.content)

    def test_no_schedule(self):
        request = self.factory.get('/')
        request.user = authenticate(username='blakr', password='blakr')
        response = profile(request)
        self.assertIn('<h4>You have no schedule, please generate one from the homepage.</h4>', response.content)

    # def test_schedule_display(self):
    #     request = self.factory.get('/')
    #     request.user = authenticate(username='blakrtest', password='blakrtest')
    #     currentUserInfo = StudentInfo.objects.get(userid = request.user)
    #     response = profile(request)
    #     self.assertIn(currentUserInfo.schedule, response.content)

class ScheduleTests(TestCase):
    fixtures = ['myADVISE.json']
