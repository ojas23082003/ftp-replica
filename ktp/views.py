import datetime
from django.shortcuts import render, redirect
from .models import IRC_Team, KtpPost, KtpComment, Ktpevent
from .forms import KtpCommentForm
from django.contrib.auth import get_user_model, login, authenticate, logout
from ftp.models import Team, Year
# Create your views here.


# def index(request):
#     if not request.user.is_authenticated:
#         if request.method == "POST":
#             admins = KtpAdmin.objects.all()
#             email = request.POST.get('email')
#             password = request.POST.get('password')
#             ktpuser = authenticate(email=email,password=password)
#             print("AAAAA=",email)
#             if ktpuser is not None:
#                 login (request, ktpuser)
#                 posts = KtpPost.objects.all().order_by('-date')
#                 print("SO=poooooooo",ktpuser)
#                 return render(request, 'ktp/index.html', {"posts": posts})
#             else:
#                 return redirect('ktp:index')
#         else:
#             print("AAAAA=")
#             posts = KtpPost.objects.all().order_by('-date')
#             return render(request, 'ktp/index.html', {"posts": posts})
#     print("AAAAAAAAAAAAAAAAAAAA=")
#     posts = KtpPost.objects.all().order_by('-date')
#     return render(request, 'ktp/index.html', {"posts": posts})

def index(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            # admins = KtpAdmin.objects.all()
            email = request.POST.get('email')
            password = request.POST.get('password')
            username = email.split("@")[0]
            ktpuser = authenticate(username=username, password=password)
            print(email)
            print(ktpuser)
            if ktpuser is not None and ktpuser.is_irc:
                login(request, ktpuser)
                posts = KtpPost.objects.all().order_by('-date')
                print("Welcome", ktpuser)
                return redirect('ktp:index')
            else:
                return redirect('ktp:index')
        else:
            print("Some trouble Aaaa=")
            posts = KtpPost.objects.all().order_by('-date')
            return render(request, 'ktp/index.html', {"posts": posts})
    print("Welcome IRC member!")
    posts = KtpPost.objects.all().order_by('-date')
    categ = Ktpevent.objects.all()
    return render(request, 'ktp/index.html', {"posts": posts, "categ": categ})


def about(request):
    if request.user.is_authenticated:
        yr = request.POST.get("year")
        if not yr:
            yr = "2022"
        print(yr)
        year = int(yr[2:])
        year_ = str(year) + "-" + str(year+1)
        print(Team.objects.all())
        yearobj = Year.objects.filter(year=year)
        team = Team.objects.filter(year=yearobj[0])

        print(team)
        Gsec = []

        leng = len(team)
        return render(request, 'ktp/about.html', {"team": team, "length": leng, "year": year_})
    else:
        return redirect("ktp:index")


def blog(request):
    posts = KtpPost.objects.all().order_by('-date')
    if request.user.is_authenticated:
        ktpevents = Ktpevent.objects.all()
        li_2 = []
        li_2.append("all")
        for events in ktpevents:
            if events.event != "all":
                li_2.append(events)
        return render(request, 'ktp/blog.html', {"posts": posts, "categ": li_2, "val": "all"})
    else:
        return redirect("ktp:index")


def post(request, post_id):
    posts = KtpPost.objects.all().order_by('-date')
    post = KtpPost.objects.get(id=post_id)
    comments = KtpComment.objects.filter(post=post_id).order_by('-date')
    if request.user.is_authenticated:
        return render(request, 'ktp/post.html', {"posts": posts, "post": post, "comments": comments})
    else:
        return render(request, 'ktp/index.html', {})


def contact(request):
    if request.user.is_authenticated:
        return render(request, 'ktp/contact.html', {})
    else:
        return redirect("ktp:index")


def add_comment(request):
    comment_params = request.POST

    _mutable = comment_params._mutable
    comment_params._mutable = True
    comment_params['date'] = datetime.datetime.now()
    comment_params._mutable = _mutable

    if request.method == 'POST':
        comment_form = KtpCommentForm(data=comment_params)
        if comment_form.is_valid():
            comment_form.save()
    else:
        comment_form = KtpCommentForm()

    return redirect("/ktp/post/" + comment_params["post"])


def add_post(request):
    if request.method == 'POST':
        date = datetime.datetime.now()
        by = request.POST.get('fname')
        categ = request.POST.get('category')
        sub = request.POST.get('subject')
        con = request.POST.get('content')
        img = request.FILES.get('exampleFormControlFile1', None)
        file = request.FILES.get('file', None)
        # print(cat)
        KtpPost.objects.create(date=date, by=by, category=categ,
                               subject=sub, content=con, photo=img, file=file)
    return redirect("ktp:index")


def logout_user(request):
    logout(request)
    return redirect('ktp:index')


def add_filter(request):
    if request.method == 'POST':
        cat_filter = str(request.POST.get('Filter'))
        if cat_filter == "all":
            return redirect("ktp:blog")
        print(cat_filter)
        events = KtpPost.objects.all().order_by('-date')
        li = []
        for eve in events:
            if eve.category == cat_filter:
                li.append(eve)
    ktpevents = Ktpevent.objects.all()
    first = Ktpevent.objects.get(event=cat_filter)
    li_2 = []
    li_2.append(first)
    for events in ktpevents:
        if events != first:
            li_2.append(events)
    li_2.append("all")
    return render(request, 'ktp/blog.html', {"posts": li, "categ": li_2, "val": cat_filter})
