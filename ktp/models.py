from statistics import mode
from unicodedata import category
import uuid
from django.db import models

# Create your models here.


class Ktpevent(models.Model):
    event = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.event)


class KtpPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(null=True)
    by = models.CharField(max_length=500, null=True, blank=True)
    category = models.CharField(max_length=500, null=True, blank=True)
    subject = models.CharField(max_length=500, null=True, blank=True)
    content = models.TextField(max_length=5000, null=True, blank=True)
    photo = models.ImageField(upload_to='ktp_posts', null=True)
    file = models.FileField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

class KtpComment(models.Model):
    date = models.DateField(null=True)
    by = models.CharField(max_length=500, null=True, blank=True)
    email = models.CharField(max_length=500, null=True, blank=True)
    subject = models.CharField(max_length=500, null=True, blank=True)
    content = models.TextField(max_length=5000, null=True, blank=True)
    post = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return str(self.id)

class IRC_Team(models.Model):
    name = models.CharField(max_length=500, null=True, blank=True)
    Position = models.CharField(max_length=500, null=True, blank=True)
    Tenure_starting_year = models.CharField(max_length=10, default=20)
    contact = models.CharField(max_length=500, default='+91 ')
    image = models.ImageField(upload_to='Team_image', null=True)

    def __str__(self):
        return str(self.name + " | " + str(self.Tenure_starting_year))
