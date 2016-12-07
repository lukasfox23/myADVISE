from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from views import index, login, create
from myADVISE.forms import LoginForm, UserForm
from models import FlightPlan, StudentInfo
from datetime import datetime
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
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        FlightPlan.objects.create(flightplanID = 1, content = 'test', major = 'BE', majorname = 'Bio-engineering', graddate = datetime.now())

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
        self.assertEqual(userFlightPlan.progress, str(userPlan[0]))
        self.assertEqual(userFlightPlan.schedule, 'none')
        self.assertEquals(200, response.status_code)
        self.assertIn('<p>Optimize your schedule making process!</p>', response.content)
