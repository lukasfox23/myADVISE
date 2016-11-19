from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^create/$', views.create, name='create'),
    url(r'^profile/$', views.profile, name='profile'),
]
