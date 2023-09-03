from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.contrib.auth.models import User
from .models import *


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'password1', 'password2')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class CustomUserDomainForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['username', 'email']


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        exclude = ['username', 'review']


# UNCOMMENT FROM HERE

class TopicForm(forms.Form):

    selectfield = forms.MultipleChoiceField()
    inputfield = forms.CharField()

    def __init__(self, topiclist, *args, **kwargs):
        super(TopicForm, self).__init__(*args, **kwargs)
        # print("called")
        topics = RequestedTopic.objects.all().filter(verified=True).values()
        topics = [i for i in topics if i not in topiclist]

        options = []
    # i=0
        for topic in topics:
            options += [(str(topic['id']), topic['topicName'])]

        options += [('0', 'Other')]
        # print(options)
        self.fields['selectfield'].choices = options

# UNCOMMENT UPTO HERE


class ProfForm(forms.ModelForm):

    class Meta:
        model = Professor
        fields = '__all__'


class AnuForm(forms.ModelForm):

    class Meta:
        model = Anu
        fields = '__all__'

class EPFLForm_2022(forms.ModelForm):

    class Meta:
        model = EPFL
        fields = '__all__'


class AnuForm_2022(forms.ModelForm):

    class Meta:
        model = Anu_2022
        fields = '__all__'


class GKFForm(forms.ModelForm):

    class Meta:
        model = gkf_appli
        fields = '__all__'


class ScholarshipForm2k23(forms.ModelForm):

    class Meta:
        model = scholarship2k23_appli
        fields = '__all__'


class SAIPForm(forms.ModelForm):

    class Meta:
        model = SAIP
        fields = '__all__'


class DyutiForm(forms.ModelForm):

    class Meta:
        model = Dyuti
        fields = '__all__'


class HultForm(forms.ModelForm):

    class Meta:
        model = Hult
        fields = '__all__'


class ProfileFormNew(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        # fields = ('fullname', 'department', 'contact', 'year', 'alt_email', 'passport', 'transcript', 'cgpa', 'cv', 'photo', 'rollno', 'review')


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('professor_name', 'university', 'project_name', 'project_detail', 'project_image', 'prerequisite',
                  'stipend', 'currency', 'project_time', 'display', 'special', 'deadline', 'tags', 'project_mode')


class ScholarshipForm(forms.ModelForm):
    class Meta:
        model = Scholarship_appli
        fields = '__all__'


class PreRequisiteForm(forms.ModelForm):
    class Meta:
        model = PreRequisite
        fields = ('pg', 'ug', 'year', 'department')


class FeedBackForm(forms.ModelForm):
    class Meta:
        model = FeedBack_PROF
        fields = '__all__'


class FeedBackFormStu(forms.ModelForm):
    class Meta:
        model = FeedBack_stu
        fields = '__all__'
