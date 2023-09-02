from django.contrib import admin
from django.urls import re_path
from . import views

app_name = 'mailing_app'

urlpatterns = [
    re_path(r'^mail/$', views.mail, name='mail'),
    re_path(r'^step1/$', views.step0, name='step1'),
    re_path(r'^step2/$', views.step1, name='step2'),
]
