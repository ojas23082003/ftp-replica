from django.urls import re_path
from django.contrib import admin
from django.views.generic import TemplateView
from .import views

app_name = 'ktp'


urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^about/$', views.about, name='about'),
    re_path(r'^blog/$', views.blog, name='blog'),
    re_path(r'^post/(?P<post_id>[0-9a-f-]+)/$', views.post, name='post'),
    re_path(r'^add_comment/$', views.add_comment, name='add_comment'),
    re_path(r'^add_post/$', views.add_post, name='add_post'),
    re_path(r'^add_post/filter$', views.add_filter, name='add_filter'),
    re_path(r'^logout_user/$', views.logout_user, name='logout_user'),
]
