from django.contrib import admin
from django.urls import include, re_path
from . import views

app_name = 'master'

urlpatterns = [
    re_path(r'^links/', views.links, name='links'),
]