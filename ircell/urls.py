"""ircell URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, re_path
# from django.conf.urls import url, include, handler404
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from ftp import views
# from ktp import views
from django.views.generic.base import RedirectView
from django.shortcuts import render
from mailing_app import views as mailing_views



urlpatterns = [
      re_path(r'^admin/', admin.site.urls),
    #   re_path(r'^ftp/', views.index, name='index'),

      re_path(r'^saip', views.saip_form, name='saip'),
      re_path(r'^notice$', views.notice, name='notice'),
      re_path(r'^ktp/', include('ktp.urls', namespace='ktp'), name='ktp'),
    #   re_path(r'^ktp/form_post', views.post_form , name='form_post'),
      re_path(r'^ftp/', include('ftp.urls', namespace='ftp'), name='ftp'),
      re_path(r'^ftp/portal/login/$', RedirectView.as_view(url='https://ircell.iitkgp.ac.in/ftp/login/'), name='redirectindex'),
      re_path(r'^composemail/', mailing_views.composemail, name='composemail'),
      re_path(r'^replymail/', mailing_views.replymail, name='replymail'),
      re_path(r'^replymailall/', mailing_views.replymailall, name='replymailall'),
      re_path(r'^replymailsend/', mailing_views.replymailsend, name='replymailsend'),
      re_path(r'^attachment_open/', mailing_views.attachment_open, name='attachment_open'),
      re_path(r'^delete_mail/', mailing_views.delete_mail, name='delete_mail'),
      re_path(r'^massmailindex/', mailing_views.index, name='massmail'),
      re_path(r'^massmailindexitr/(\d+)/$', mailing_views.indexrepeat, name='massmailrepeat'),
      re_path(r'^massmail/', include('mailing_app.urls', namespace='mailing_app'), name='mailing_app'),
      re_path(r'', include('master.urls', namespace='master'), name='master'),
      re_path(r'^search/', mailing_views.searchh, name='search'),
      re_path(r'^massmailindexSpamFolder/', mailing_views.spamm, name='spam'),
      re_path(r'^massmailindexSpamFolderitr/(\d+)/$', mailing_views.indexrepeatt, name='massmailrepeatSpam'),
      re_path(r'^hult/info/$', views.hult_info, name='hult_info'),
      re_path(r'^hult/info/show_info/(?P<id>\d+)', views.show_info, name='show_info'),
      re_path(r'^hult/register/$', views.hult_register, name='hult_register'),
      # re_path(r'^dyuti/$', views.dyuti, name='dyuti'),
      re_path(r'^hult/$', views.hult, name='hult'),
      re_path(r'^anu/$', views.view_anu_2022, name='anu_2022'),
      re_path(r'^epfl/$', views.view_epfl_2022, name='epfl_2022'),

      re_path(r'event/(?P<id>[0-9])/$', views.event, name='event'),
      re_path(r'noticeboard/(?P<id>[0-9])/$', views.noticeboardNotice, name='noticeboardNotice'),
      re_path(r'noticeboard', views.noticeboard, name='noticeboard'),
      re_path(r'^ftp/export_scholarships/$', views.export_scholarships, name='export_scholarships'),
      re_path(r'^$', views.home, name='home'),
      
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'ftp.views.handler404'
