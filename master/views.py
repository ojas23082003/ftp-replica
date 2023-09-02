from django.shortcuts import render
from .models import *

# Create your views here.
def links(request):
    all_links = Link.objects.all()
    return render(request, 'master/links/index.html', {'links': all_links})