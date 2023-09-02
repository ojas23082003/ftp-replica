from django.contrib import admin
from .import views
from django.views.generic import TemplateView
from django.urls import include, re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from ftp import views as core_views
from ftp.views import Add_tags

app_name = 'ftp'

urlpatterns = [
    re_path(r'^test', views.test),
    # re_path(r'^projects/anu/apply', views.personalNotice, name='personalNotice'),
    re_path(r'^projects/notices', views.personalNotice, name='personalNotice'),
    re_path(r'^projects/anu/success', TemplateView.as_view(
        template_name='ftp/ProjectsPage/anu_apply_confirm.html'), name='anu_projects_confirmation'),
    re_path(r'^projects/epfl/success', TemplateView.as_view(
        template_name='ftp/ProjectsPage/epfl_apply_confirm.html'), name='epfl_projects_confirmation'),
    re_path(r'^projects/anu', views.view_anu_projects, name='anu_projects'),
    re_path(r'^projects/new_anu', views.view_anu_2022, name='anu_projects_new'),
    re_path(r'^projects/saip/success', TemplateView.as_view(
        template_name='ftp/ProjectsPage/saip_apply_confirm.html'), name='saip_projects_confirmation'),
    re_path(r'^temp/', views.temp, name='temp'),
    re_path(r'^$', views.index, name='index'),




    re_path(r'^register/', views.register, name='register'),
    re_path(r'^dashboard_mail/$', views.dashboard_mail, name='dashboard_mail'),
    re_path(r'^login/$', views.login_user, name='login_user'),
    re_path(r'^session/$',
            TemplateView.as_view(template_name='ftp/session.html'), name='session'),
    re_path(r'^profile/$', views.view_profile, name='view_profile'),
    re_path(r'^logout_user/$', views.logout_user, name='logout_user'),
    re_path(r'^create_profile/$', views.create_profile, name='create_profile'),
    re_path(r'^resend_activation/(?P<user_id>[0-9a-f-]+)/$',
            views.resendActivation, name='resend_activation'),
    re_path(r'^password_reset/', auth_views.PasswordResetView,
            name='password_reset'),
    re_path(r'^account_activation_sent/$',
            auth_views.PasswordResetConfirmView, name='account_activation_sent'),
    re_path(
        r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    re_path(r'^projects/$', views.view_projects, name='projects'),
    re_path(r'^project_info/$', views.project_details, name='project_info'),
    re_path(r'^apply_project/(?P<project_id>[0-9a-f-]+)/$',
            views.view_apply_project, name='view_apply_project'),
    re_path(r'^scholarships/$', views.view_scholarships, name='scholarships'),
    re_path(r'^scholarships_new/$', views.view_scholarships_new,
            name='scholarships_new'),
    re_path(r'^scholarships_new/(?P<scholarship_id>[0-9a-f-]+)/$',
            views.view_scholarship_apply, name='scholarship_apply'),
    re_path(r'^scholarships/2023/$', views.apply_scholarships_2k23,
            name='apply_scholarships_2k23'),
    re_path(r'^scholarships/gkf/$', views.apply_gkf, name='apply_gkf'),
    re_path(r'^scholarships/gkf/success/$', TemplateView.as_view(
        template_name='ftp/Scholarship/gkf_apply_confirm.html'), name='gkf_confirmation'),
    re_path(r'^scholarships/scholarships/2023/success/$', TemplateView.as_view(
        template_name='ftp/Scholarship/scholarships_2k23_apply_confirm.html'), name='scholarships_2k23_confirmation'),
    re_path(r'^scholarships/gkf/export/all/$',
            views.export_gkf, name='export_gkf'),
    re_path(r'^export_emails/$',
            views.export_emails, name='export_emails'),
    re_path(r'^scholarships/apply/(?P<scholarship_id>[0-9a-f-]+)/$',
            views.apply_scholarship, name='apply_scholarship'),
    re_path(r'^scholarships/yourscholarships/$',
            views.yourscholarships, name='yourscholarships'),
    re_path(r'^results/$', views.view_results, name='results'),
    re_path(r'^projects/(?P<project_id>[0-9a-f-]+)/$',
            views.apply_project, name='apply_project'),
    re_path(r'^applications/$', views.already_applied, name='yourapplications'),
    re_path(r'^professors/(?P<project_id>[0-9a-f-]+)/$',
            views.applied_students, name='applied_students'),
    re_path(
        r'^professors/(?P<project_id>[0-9a-f-]+)/profile/(?P<profile_id>[0-9a-f-]+)/$', views.view_frame, name='iframe'),
    re_path(r'^favorites/$', views.view_favorite, name='bookmarked'),
    re_path(r'^scholarships/yourscholarships/$',
            views.yourscholarships, name='yourscholarships'),
    re_path(r'^favorites/add_favourite/(?P<pk>[0-9a-f-]+)/$',
            views.add_favorite, name='add_favorite'),
    re_path(r'^domain_change/$', views.domain_change, name='domainchange'),
    re_path(r'^domain_reset_form/$',
            views.domain_reset_form, name='domainresetform'),
    re_path(r'^forgot-send_email/$', views.forgotpass, name='forgotpassword'),
    re_path(
        r'^forgot/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.pass_reset, name='forgottoken'),
    re_path(r'^forgot-password_reset_done/$', views.pass_reset_done,
            name='forgot_password_reset_done'),
    re_path(r'^professor_add/$', views.get_detail, name="prof_details"),
    re_path(r'^profile/edit/$', views.edit_profile, name='edit_profile'),
    re_path(r'^dashboard_projects/$',
            views.admin_projects, name='admin_projects'),
    re_path(r'^dashboard_projects/project_csv/$',
            views.project_csv, name='project_csv'),
    re_path(r'^dashboard_projects/professor_csv/$',
            views.professor_csv, name='professor_csv'),
    re_path(r'^dashboard_projects/applicants/$',
            views.applicant_profile, name='applicant_profile'),
    re_path(r'^dashboard_projects/teams/$',
            views.hult_profile, name='hult_profile'),
    re_path(r'^dashboard_projects/mail/$',
            views.applicant_mail, name='applicant_mail'),
    re_path(r'^dashboard_profiles/applicants_edit/(?P<pk>[0-9a-f-]+)/$',
            views.applicant_profile_edit.as_view(), name='applicant_profile_edit'),
    re_path(r'^dashboard_scholarship/$',
            views.admin_scholarship, name='admin_scholarship'),
    re_path(r'^dashboard_scholarship/applicants/$',
            views.scholarship_applicant_profile, name='scholarship_applicant_profile'),
    re_path(r'^dashboard_scholarship/gkf_applicants/$',
            views.gkf_scholarship_applicant_profile, name='gkf_scholarship_applicant_profile'),
    # re_path(r'^dashboard_scholarships/delete/(?P<pk>[0-9a-f-]+)/$', views.scholarship_delete,name="scholarship_delete"),
    re_path(r'^dashboard_scholarships/create/$',
            views.admin_scholarships_create, name="admin_scholarships_create"),
    re_path(r'^dashboard_scholarships/edit/(?P<pk>[0-9a-f-]+)$',
            views.ScholarshipUpdate.as_view(), name="admin_scholarships_edit"),
    re_path(r'^dashboard_scholarships/change/$',
            views.change_display_scho, name='change_display_scho'),
    # re_path(r'^dashboard_projects/export/$', views.export_project, name='admin_projects_export'),
    re_path(r'^dashboard_projects/export/(?P<pk>[0-9a-f-]+)/$',
            views.export_applied_list, name='admin_applied_list_export'),
    re_path(r'^dashboard_anu_projects/export/all/$',
            views.export_applied_anu_all_list, name='admin_applied_anu_all_list_export'),
    re_path(r'^dashboard_anu_projects/export/(?P<project_name>.+)/$',
            views.export_applied_anu_list, name='admin_applied_anu_list_export'),
    re_path(r'^dashboard_projects/scholarship_csv/$',
            views.scholarship_csv, name='scholarship_csv'),
    re_path(r'^dashboard_profiles/export/$',
            views.export_profile, name='admin_profiles_export'),
    re_path(r'^dashboard_profiles/export_topics/$',
            views.export_topics, name='admin_topics_export'),
    re_path(r'^dashboard_profiles/export_mail_ids/$',
            views.export_mail_ids, name='admin_mail_ids_export'),
    re_path(r'^dashboard_profiles/clear-search/$',
            views.clear_search, name='clear_search'),
    re_path(r'^dashboard_profiles/search/$',
            views.search_profile, name='profile_search'),
    re_path(r'^dashboard_dyuti/export/$',
            views.export_dyuti, name='admin_dyuti_export'),
    re_path(r'^dashboard_projects/edit/prereq/(?P<name>.+)/$',
            views.edit_prereq, name='admin_prereqs_edit'),
    re_path(r'^dashboard_hult/export/$',
            views.export_hult, name='admin_hult_export'),
    re_path(r'^dashboard_saip/export/$',
            views.export_saip, name='admin_saip_export'),
    re_path(r'^dashboard_profiles/$',
            views.admin_profiles, name='admin_profiles'),
    re_path(r'^dashboard_addresult/(?P<pk>[0-9a-f-]+)/$',
            views.addresult, name='admin_Addresult'),
    re_path(r'^dashboard_projects/create/$',
            views.project_create, name='admin_projects_create'),
    re_path(r'^dashboard_profiles/create/$',
            views.profile_create, name='admin_profiles_create'),
    re_path(r'^dashboard_projects/edit/(?P<pk>[0-9a-f-]+)/$',
            views.ProjectUpdate.as_view(), name='admin_projects_edit'),
    re_path(r'^dashboard_profiles/edit/(?P<pk>[0-9a-f-]+)/$',
            views.ProfileUpdate.as_view(), name='admin_profiles_edit'),
    # re_path(r'^dashboard_projects/delete/(?P<pk>[0-9a-f-]+)/$', views.project_delete, name='admin_projects_delete'),
    #re_path(r'^dashboard_profiles/delete/(?P<pk>[0-9a-f-]+)/$', views.profile_delete, name='admin_profiles_delete'),
    re_path(r'^dashboard_projects/change_display/$',
            views.project_display_change, name='change_display'),
    re_path(r'^dashboard_projects/change_prof_display/$',
            views.change_prof_display, name='change_prof_display'),
    re_path(r'^dashboard_dyuti/$', views.admin_dyuti, name='admin_dyuti'),
    re_path(r'^dashboard_hult/$', views.admin_hult, name='admin_hult'),
    re_path(r'^dashboard_hult/timer/$',
            views.admin_hult_timer, name='admin_hult_timer'),
    re_path(r'^dashboard_professors/$',
            views.admin_professors, name='admin_professors'),
    re_path(r'^dashboard_professors/edit/(?P<pk>[0-9a-f-]+)/$',
            views.ProfessorUpdate.as_view(), name='admin_professors_edit'),
    re_path(r'^dashboard_professors/export/$', views.export_professor,
            name='admin_professor_list_export'),
    re_path(r'^dashboard_applications/$',
            views.admin_applications, name='admin_applications'),
    re_path(r'^dashboard_applications/give_access$',
            views.give_access, name='give_access'),
    re_path(r'^dashboard_projects/import/$',
            views.import_project, name='admin_projects_import'),
    re_path(r'^dashboard_projects/import/(?P<project_id>[0-9a-f-]+)/$',
            views.import_project_create, name='import_project_create'),
    re_path(
        r'^dashboard_projects/Project_Tag/delete-tags/(?P<pk>[0-9a-f-]+)/$', views.deletetags, name='delete-tags'),
    re_path(r'^dashboard_log/$', views.admin_logs, name='admin_logs'),
    re_path(r'^professor_feedback/$',
            views.feedback_form, name="prof_feedback"),
    re_path(r'^student_feedback/$',
            views.feedback_form_stu, name="stu_feedback"),
    re_path(r'^dashboard_projects/Project_Tag/$',
            views.Add_tags, name='admin_project_tag'),
    re_path(
        r'^dashboard_projects/status/(?P<project_id>[0-9a-f-]+)/$', views.showstatus, name='admin_editstatus'),
    re_path(r'^dashboard_projects/status/d/(?P<project_id>[0-9a-f-]+)/$',
            views.status_default, name='admin_defaultstatus'),
    re_path(
        r'^dashboard_projects/resultss/(?P<project_id>[0-9a-f-]+)/$', views.resultss, name='admin_results'),
    re_path(r'^blogs/$',
            views.blogs, name='blogs'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
