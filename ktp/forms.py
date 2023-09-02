from django.contrib.auth.models import User
from django import forms
from .models import KtpPost, KtpComment


class KtpPostForm(forms.ModelForm):
    class Meta:
        model = KtpPost
        fields = ['date', 'by', 'category', 'subject', 'content', 'photo']


class KtpCommentForm(forms.ModelForm):
    class Meta:
        model = KtpComment
        fields = ['post', 'date', 'by', 'email', 'subject', 'content']
