from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^progress/$', views.progress, name='progress'),
    url(r'^create/$', views.create, name='create'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^schedule/$', views.schedule, name='schedule'),
]
