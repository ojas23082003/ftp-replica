from django.contrib import admin
from . models import KtpPost, KtpComment, Ktpevent, IRC_Team

admin.site.register(KtpPost)
admin.site.register(KtpComment)
admin.site.register(Ktpevent)
admin.site.register(IRC_Team)
