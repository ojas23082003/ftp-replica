from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
import csv
from django.http import HttpResponse
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import *


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'username', 'is_irc')
    list_filter = ('is_irc', 'is_staff', 'is_superuser', 'is_active')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_irc', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active', 'is_irc')}
         ),
    )


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'fullname']
    search_fields = ('fullname',)

class HultInfoAdmin(admin.ModelAdmin):
    model = HultInfo
    fields = ['title', 'subtitle', 'desc', 'links']
    list_display = ('title', 'subtitle', 'links')

class InfoLinkAdmin(admin.ModelAdmin):
    model = InfoLink
    list_display = ('title', 'subtitle')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Project)
admin.site.register(Application)
admin.site.register(ProjectDomain)
admin.site.register(Professor)
admin.site.register(Dyuti)
admin.site.register(Hult)
admin.site.register(Result)
admin.site.register(Scholarship)
admin.site.register(Scholarship_appli)
admin.site.register(gkf_appli)
admin.site.register(scholarship2k23_appli)
admin.site.register(PreRequisite)
admin.site.register(FeedBack_PROF)
admin.site.register(FeedBack_stu)
admin.site.register(Notice)
admin.site.register(ProjectTag)
admin.site.register(Anu)
admin.site.register(SAIP)
admin.site.register(EPFL)
admin.site.register(Anu_2022)
admin.site.register(RequestedTopic)
admin.site.register(Noticeboard)
admin.site.register(Event)
admin.site.register(EventImage)
admin.site.register(Type)
admin.site.register(Testimonials)
admin.site.register(Team)
admin.site.register(Year)
admin.site.register(HultInfo, HultInfoAdmin)
admin.site.register(HultPoster)
admin.site.register(InfoLink, InfoLinkAdmin)