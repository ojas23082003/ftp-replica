import csv
import datetime
import os

from django.contrib import messages
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.urls import reverse_lazy, resolve
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_protect


from django.conf import settings

from .forms import *
from .models import *
from .tokens import account_activation_token, forgot_password_token


def test(request):
    return render(request, 'ftp/ProjectsPage/projects2023.html')


def personalNotice(request):
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(username=request.user)
            status = []
            pendingNotifications = []

            applications = Application.objects.filter(profile=profile)
            for app in applications:
                status.append([app.project, app.status])

            for s in status:
                statusId = s[0].id.urn[9:]
                if statusId + s[1] not in profile.viewedNotifications.split(','):
                    pendingNotifications.append(s)
                    profile.viewedNotifications = profile.viewedNotifications + \
                        statusId + s[1] + ','
                    profile.save()

            return render(request, 'ftp/ProjectsPage/notifications.html', {'prof': profile, 'status': status, 'pendingNotifications': pendingNotifications})
        except Profile.DoesNotExist:
            return redirect('ftp:create_profile')
    else:
        return redirect('ftp:login_user')


def temp(request):
    return render(request, 'ftp/profile/view_profile.html')


def handler404(request, exception):
    # response = render(request, '404.html')
    # response.status_code = 404
    return render(request, '404.html')


def home(request):
    events = Event.objects.filter(display=True).order_by('-date')
    testimonials_irc = Testimonials.objects.filter(
        display=True, type__name="ftp", year__year=2022)
    team22 = Team.objects.filter(display=True, year__year=2022)
    return render(request, 'ftp/home/index2023.html', {'events': events, 'testimonials_irc': testimonials_irc, 'team22': team22})


def event(request, id):
    event = Event.objects.filter(id=id, display=True).order_by('-date')
    events = Event.objects.filter(display=True).order_by('-date')
    eventImages = EventImage.objects.filter(event__id=id)
    return render(request, 'home/event.html', {'event': event[0], 'events': events, 'eventImages': eventImages})


def noticeboardNotice(request, id):
    notice = Noticeboard.objects.filter(id=id).order_by('-date')
    notices = Noticeboard.objects.filter().order_by('-date')
    return render(request, 'home/noticeboardNotice.html', {'notice': notice[0], 'notices': notices})


def noticeboard(request):
    # return redirect('ftp:login_user')
    notices = Noticeboard.objects.filter().order_by('-date')
    notices4 = []
    for i in range(len(notices)):
        if i % 4 == 0:
            notice4 = []
            for j in range(4):
                if i+j < len(notices):
                    notice4.append(notices[i+j])
            notices4.append(notice4)
    success = True
    if not notices:
        success = False
    return render(request, 'home/notice.html', {'success': success, 'notices': notices, 'notices4': notices4})


def index(request):
    date_threshold = datetime.date.today() - datetime.timedelta(days=5)
    testimonials_ftp = Testimonials.objects.filter(
        display=True, type__name="ftp", year__year=2022)
    notices = Notice.objects.filter(date__gte=date_threshold).order_by('-date')
    team = Team.objects.filter(display=True, year__year=2022)
    team3 = []
    for i in range(len(team)):
        if i % 3 == 0:
            tm3 = []
            for j in range(3):
                if i+j < len(team):
                    tm3.append(team[i+j])
            team3.append(tm3)
    try:
        if request.user.is_authenticated:
            profile = Profile.objects.get(username=request.user)
            pendingNotifications = []
            for notice in notices:
                noticeId = notice.id.urn[9:]
                if noticeId not in profile.viewedNotifications.split(','):
                    pendingNotifications.append(notice)
                    profile.viewedNotifications = profile.viewedNotifications + noticeId + ','
                    profile.save()
        else:
            pendingNotifications = []
    except Profile.DoesNotExist:
        pendingNotifications = []

    success = True
    if not notices:
        success = False
    return render(request, 'ftp/home/index2023.html', {'success': success, 'pendingNotifications': pendingNotifications, 'notices': notices, 'testimonials_ftp': testimonials_ftp, 'team3': team3})


def notice(request):
    # return redirect('ftp:login_user')
    notices = Notice.objects.all().order_by('-date')
    success = True
    if not notices:
        success = False
    return render(request, 'ftp/home/notice_board.html', {'success': success, 'notices': notices})


def register(request):
    # return redirect('ftp:login_user')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        try:
            query = CustomUser.objects.get(
                username=request.POST.get("username"))
            if not query.is_active:
                query.email = query.username + request.POST.get("domain")
                query.save()
                return redirect('ftp:resend_activation', query.id)
            else:
                print("Already exists.")
                return render(request, 'ftp/login/register.html', {'form': form, 'error': 'A user with that username already exists.'})
        except CustomUser.DoesNotExist:
            if form.is_valid():
                print('form valid')
                user = form.save(commit=False)
                print(user)
                email = str(form.cleaned_data.get('username')).lower()
                if ("@iitkgp.ac.in" not in email) and ("@kgpian.iitkgp.ac.in" not in email):
                    if "@" in email:
                        print('Do not use @')
                        return render(request, 'ftp/login/register.html', {'error': 'Please use @iitkgp.ac.in or @kgpian.iitkgp.ac.in email'})
                    email = email + str(request.POST.get('domain'))
                if ("@iitkgp.ac.in" in email) or ("@kgpian.iitkgp.ac.in" in email):
                    username = email.split('@')[0]
                password1 = form.cleaned_data.get('password1')
                password2 = form.cleaned_data.get('password2')
                user.username = username.lower()
                try:
                    query = CustomUser.objects.get(username=user.username)
                    if not query.is_active:
                        return redirect('ftp:resend_activation', query.id)
                    else:
                        print("Already exists.")
                        return render(request, 'ftp/login/register.html', {'form': form, 'errors': form.errors, 'error': 'A user with that username already exists.'})
                except CustomUser.DoesNotExist:
                    user.email = email
                    user.is_active = False
                    user.save()
                    current_site = get_current_site(request)
                    subject = 'FTP: Account Activation'
                    message = render_to_string('ftp/account_activation_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': account_activation_token.make_token(user),
                    })
                    print('--------------------------\n', urlsafe_base64_encode(
                        force_bytes(user.pk)), '---------------------------\n')
                    email = EmailMessage(
                        subject, message, settings.EMAIL_HOST_USER, to=[
                            user.email]
                    )
                    email.send(fail_silently=True)
                    print(message)
                    return render(request, 'ftp/login/Email_sent.html', context={'email': user.email, 'user_id': user.id})
            else:
                print(form.errors)
                return render(request, 'ftp/login/register.html', {'form': form, 'errors': form.errors})

    else:
        form = CustomUserCreationForm()
        return render(request, 'ftp/login/login2023.html', {'form': form})


def domain_change(request):
    return render(request, 'ftp/login/domain_change.html')


def domain_reset_form(request):
    User = get_user_model()
    form = CustomUserDomainForm(request.POST)
    if form.is_valid():
        # print("hello \n")
        email = str(form.cleaned_data.get('username')).lower()
        # print(email)
        if request.method == 'POST':
            if ("@iitkgp.ac.in" not in email) and ("@kgpian.iitkgp.ac.in" not in email):
                # if "@" in email:
                #     print('Do not use @')
                return render(request, 'ftp/login/domain_change.html', {'error': 'Please use @iitkgp.ac.in or @kgpian.iitkgp.ac.in email'})
            if ("@iitkgp.ac.in" in email) or ("@kgpian.iitkgp.ac.in" in email):
                username = email.split('@')[0]
            try:
                query = CustomUser.objects.get(username=username)
                user = User.objects.get(username=username)
                if query.is_active:
                    print("Already exists.")
                    return render(request, 'ftp/login/register.html', {'form': form, 'error': 'This account is already active.'})
                else:
                    # if not CustomUser.DoesNotExist:
                    # print("hello PART 2 \n")
                    print(user.username)
                    # user.form.cleaned_data['email']
                    user.email = email
                    user.is_active = False
                    user.save()
                    # print(user.email)
                    current_site = get_current_site(request)
                    subject = 'FTP: Account Activation'
                    message = render_to_string('ftp/account_activation_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': account_activation_token.make_token(user),
                    })
                    print('--------------------------\n', urlsafe_base64_encode(
                        force_bytes(user.pk)), '---------------------------\n')
                    email = EmailMessage(
                        subject, message, settings.EMAIL_HOST_USER, to=[
                            user.email]
                    )
                    email.send(fail_silently=True)
                    print(message)
                    return render(request, 'ftp/login/Email_sent.html', context={'email': user.email, 'user_id': user.id})
            except CustomUser.DoesNotExist:
                print("Not registered.")
                return render(request, 'ftp/login/register.html', {'form': form, 'error': 'This account is not yet registered.'})
    else:
        return render(request, 'ftp/login/domain_change.html', {'error': 'Please use @iitkgp.ac.in or @kgpian.iitkgp.ac.in email'})


def resendActivation(request, user_id):
    print("Resending link.")
    user = CustomUser.objects.get(id=user_id)
    current_site = get_current_site(request)
    subject = 'FTP: Account Activation'
    message = render_to_string('ftp/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    email = EmailMessage(
        subject, message, settings.EMAIL_HOST_USER, to=[user.email]
    )
    email.send(fail_silently=True)
    print(message)
    return render(request, 'ftp/login/Email_sent.html', context={'email': user.email, 'user_id': user.id})


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    print(user.username, account_activation_token.check_token(user, token))
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('ftp:login_user')
    elif user is not None and user.is_active:
        return redirect('ftp:login_user')
    else:
        return HttpResponse("Link is invalid")


def new_profile(request):
    # return redirect('ftp:login_user')
    if not request.user.is_authenticated:
        return render(request, 'login.html')
    else:
        if len(Profile.objects.filter(username=request.user.id)) == 0:
            roll = request.user.username
            dep = roll[2:4]

            pr_year = 22 - int(roll[0:2])
            # is_allowed = (int(roll[4]) >= 6)
            # if pr_year > 1 or is_allowed:
            # logout(request)
            # form = CustomUserCreationForm()
            # return render('ftp/login/register.html', {'form': form}, context={'errors': 'Not allowed to register'})
            # print(pr_year)
            deps = {
                'AE': 'Aerospace Engineering',
                'AG': 'Agricultural and Food Engineering',
                'AR': 'Architecture and Regional Planning',
                'BT': 'Biotechnology',
                'CH': 'Chemical Engineering',
                'CY': 'Chemistry',
                'CE': 'Civil Engineering',
                'CS': 'Computer Science and Engineering',
                'EE': 'Electrical Engineering',
                'EC': 'Electronics and Electrical Communication Engg.',
                'GG': 'Geology and Geophysics',
                'HS': 'Humanities and Social Sciences',
                'IM': 'Industrial and Systems Engineering',
                'MA': 'Mathematics',
                'ME': 'Mechanical Engineering',
                'MT': 'Metallurgical and Materials Engineering',
                'MI': 'Mining Engineering',
                'NA': 'Ocean Engg and Naval Architecture',
                'PY': 'Physics'}
            print(dep)

            department = deps[dep]
            print(department)
            if (pr_year == 1):
                print(str(pr_year) + 'st')
            elif (pr_year == 2):
                print(str(pr_year) + 'nd')
            elif (pr_year == 3):
                print(str(pr_year) + 'rd')
            else:
                print(str(pr_year) + 'th')

            return render(request, 'profile.html', {'roll': roll, 'department': department, 'present_year': pr_year})

        else:
            return redirect('/ftp/portal/projects/')


def login_user(request):
    if request.user.is_authenticated:
        return redirect('ftp:projects')
    if request.method == "POST":
        username = str(request.POST['email']).lower()
        if ("@iitkgp.ac.in" not in username) and ("@kgpian.iitkgp.ac.in" not in username):
            if "@" in username:
                print('Do not use @')
                return render(request, 'ftp/login/login.html', {'error': 'Please use @iitkgp.ac.in or @kgpian.iitkgp.ac.in email'})
        if ('@iitkgp.ac.in' in username) or ('@kgpian.iitkgp.ac.in' in username):
            username = username.split("@")[0]
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                try:
                    profile = Profile.objects.get(username=request.user)
                    print(profile.photo)
                    if not profile.photo:
                        messages.success(request, "Please add your photo")
                        return redirect('ftp:edit_profile')
                    if profile.updated == False:
                        return render(request, 'ftp/profile/edit_profile.html', {'updated': True, 'profile': profile})
                    return redirect('ftp:projects')
                except Profile.DoesNotExist:
                    return redirect('ftp:create_profile')
            else:
                return render(request, 'ftp/login/login.html', {'error': 'You have not activated your account, activate using the link sent to your mail.'})
        else:
            try:
                user = CustomUser.objects.get(username=username)
                if not user.is_active:
                    return render(request, 'ftp/login/login.html', {'error': 'You have not activated your account, activate using the link sent to your mail.'})
                if password != user.password:
                    return render(request, 'ftp/login/login.html', {'error': 'Incorrect Password'})
            except CustomUser.DoesNotExist:
                print('Not a registered User')
                return render(request, 'ftp/login/login.html', {'error': 'Looks like you are not registered, create a new account.'})
    else:
        return render(request, 'ftp/login/login.html')


def logout_user(request):
    logout(request)
    return redirect('ftp:login_user')


def create_profile(request):
    # return redirect('ftp:login_user')
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        try:
            profile = Profile.objects.get(username=request.user)
            return redirect('ftp:view_profile')
        except Profile.DoesNotExist:
            pass
        form = ProfileForm(request.POST or None, request.FILES or None)
        # print(form.department)
        print(request.POST.get("contact"))
        print(request.POST.get("fullname"))
        print(request.POST.get("degree_type"))
        # roll = request.user.username
        # dep = roll[2:4]
        # pr_year = 20-int(roll[0:2])

        # if(pr_year==1):
        # print(str(pr_year)+'st')
        # elif(pr_year==2):
        # print(str(pr_year)+'nd')
        # elif(pr_year):
        # print(str(pr_year)+'rd')
        # else:
        # print(str(pr_year)+'th')

        if form.is_valid():
            # print(form.errors)
            # form.save(commit=False).username = request.user.id
            make_prof = form.save(commit=False)
            # print(request.user)
            make_prof.username = request.user
            roll = make_prof.rollno
            pr_year = 22 - int(roll[0:2])
            is_allowed = (int(roll[4]) >= 4)
            # if pr_year <= 1 and not is_allowed:
            # 	logout(request)
            # 	error = 'First years are ineligible to register. Try again next year.'
            # 	request.user.is_active = False
            # 	# print(error)
            # 	return render(request, 'ftp/login/login.html', {'error': error})
            make_prof.save()

            prof = Profile.objects.filter(fullname=request.POST['fullname'])
            # print(prof)
            prof.update(review='NO', updated=True)
            # print(form.errors)
            return redirect('ftp:projects')
        else:
            print(form.errors)
            return render(request, 'ftp/profile/index.html',
                          {'roll': request.user, 'form': form, 'errors': form.errors})


def view_projects(request):
    # return redirect('ftp:login_user')
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        try:
            profile = Profile.objects.get(username=request.user)
        except Profile.DoesNotExist:
            return redirect('ftp:create_profile')

        status = []
        pendingNotifications = []

        applications = Application.objects.filter(profile=profile)
        for app in applications:
            status.append([app.project, app.status])

        for s in status:
            statusId = s[0].id.urn[9:]
            if statusId + s[1] not in profile.viewedNotifications.split(','):
                pendingNotifications.append(s)
                profile.viewedNotifications = profile.viewedNotifications + \
                    statusId + s[1] + ','
                profile.save()

        if not profile.updated:
            return redirect('ftp:logout_user')

        rem_project = Project.objects.exclude(
            id__in=[x.id for x in profile.project.all()])
        # rem_project = Project.objects.exclude(id__in=[x.project.id for x in Application.objects.filter(profile=profile)])
        current_time = datetime.datetime.now().date()
        bookmarked = Project.objects.filter(bookmarks=profile)
        for proj in rem_project:
            if current_time > proj.deadline:
                proj.display = False
                # print('qwerty')

        proj_domains = ProjectDomain.objects.all()

        success = True
        pastproject = Project.objects.all()
        for proj in rem_project:
            if proj.display:
                success = False

        print(success)


#   UNCOMMENT FROM HERE TO ENABLE REQUEST A TOPIC OPTION

        # if(profile.requestedTopic):
        # 	selected = str(profile.requestedTopic_id)
        # else:
        selected = "default"

        reqtopics = profile.topics.all().values()

        print(reqtopics)
        form = TopicForm(reqtopics)
        form.fields['selectfield'].initial = selected

        if request.POST:
            # select = request.POST.getlist('selectfield')
            select = request.POST.getlist('checks[]')

            print(select)

            if ('0' in select):
                input = request.POST['inputfield']
                topic, created = RequestedTopic.objects.get_or_create(
                    topicName=input)
                # profile.requestedTopic_id = topic.id
                # profile.save()
                topic.users.add(profile)
                if (created):
                    topic.count += 1

                topic.save()
                selected = str(topic.id)
                select.remove('0')

            for item in select:
                topic = RequestedTopic.objects.get(id=item)

                topic.users.add(profile)
                topic.count += 1
                topic.save()
            # profile.requestedTopic_id = topic.id
            # profile.save()
            selected = "default"
            profile.save()
            reqtopics = profile.topics.filter(verified=True).values()

            form1 = TopicForm(reqtopics)
            form1.fields['selectfield'].initial = selected
            print("new topic added")
            return render(request, 'ftp/ProjectsPage/projects2023.html',
                          {"success": success, 'allprojects': rem_project, 'prof': profile, 'bookmarks': bookmarked, 'pastproject': pastproject, 'proj_domains': proj_domains, 'date': current_time, 'selected': profile.selected, "pendingNotifications": pendingNotifications, "form": form1})

        for p in rem_project:
            print(p.display)
# UNCOMMENT UPTO HERE TO ENABLE REQUEST A TOPIC FEATURE
        return render(request, 'ftp/ProjectsPage/projects2023.html',
                      {"success": success, 'allprojects': rem_project, 'prof': profile, 'bookmarks': bookmarked, 'pastproject': pastproject, 'proj_domains': proj_domains, 'date': current_time, 'selected': profile.selected, "pendingNotifications": pendingNotifications, "form": form})


def project_details(request):
    # if not request.user.is_authenticated:
    #     return redirect('ftp:login_user')
    # else:
    #     try:
    #         profile = Profile.objects.get(username=request.user)
    #     except profile.DoesNotExist:
    #         return redirect('ftp:create_profile')
    success = True
    profile = []
    return render(request, 'ftp/ProjectsPage/project_details.html', {"success": success,  'prof': profile, })


def view_projects_new(request):
    # return redirect('ftp:login_user')
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        try:
            profile = Profile.objects.get(username=request.user)
        except profile.DoesNotExist:
            return redirect('ftp:create_profile')

        status = []
        pendingNotifications = []

        applications = Application.objects.filter(profile=profile)
        for app in applications:
            status.append([app.project, app.status])

        for s in status:
            statusId = s[0].id.urn[9:]
            if statusId + s[1] not in profile.viewedNotifications.split(','):
                pendingNotifications.append(s)
                profile.viewedNotifications = profile.viewedNotifications + \
                    statusId + s[1] + ','
                profile.save()

        if not profile.updated:
            return redirect('ftp:logout_user')

        rem_project = Project.objects.exclude(
            id__in=[x.id for x in profile.project.all()])
        # rem_project = Project.objects.exclude(id__in=[x.project.id for x in Application.objects.filter(profile=profile)])
        current_time = datetime.datetime.now().date()
        bookmarked = Project.objects.filter(bookmarks=profile)
        for proj in rem_project:
            if current_time > proj.deadline:
                proj.display = False
                # print('qwerty')

        proj_domains = ProjectDomain.objects.all()
        success = True
        pastproject = Project.objects.all()

        for proj in rem_project:
            if proj.display:
                success = False

        print(success)

        # if request.method=='POST':
        # 	form = TopicForm(request.POST, instance=profile)
        # 	if form.is_valid():
        # 		print(form.cleaned_data)
        # 		form.save()

        # 		return render(request, 'ftp/ProjectsPage/projects.html',{"success": success, 'allprojects': rem_project, 'prof': profile, 'bookmarks': bookmarked,'pastproject':pastproject, 'proj_domains': proj_domains, 'date':current_time, 'selected':profile.selected, "pendingNotifications": pendingNotifications,"form":form})
        # else:
        # 	form = TopicForm(instance=profile, e=topics)

    return render(request, 'ftp/ProjectsPage/projects2023.html', {"success": success, 'allprojects': rem_project, 'prof': profile, 'bookmarks': bookmarked, 'pastproject': pastproject, 'proj_domains': proj_domains, 'date': current_time, 'selected': profile.selected, "pendingNotifications": pendingNotifications})


def view_apply_project(request, project_id):
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        try:
            project = Project.objects.get(id=project_id)
            profile = Profile.objects.get(username=request.user)
            return render(request, 'ftp/ProjectsPage/apply_project.html',
                          {'prof': profile, 'p': project})
        except IndexError:
            return redirect('ftp:projects')


def view_anu_projects(request):
    # return redirect('ftp:login_user')
    if (request.method == "POST"):
        form = AnuForm(request.POST or None, request.FILES or None)
        print(request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Applied successfully!')
            return redirect('ftp:anu_projects_confirmation')
        else:
            print(form.errors)
            return render(request, 'ftp/ProjectsPage/anu_apply.html', {'form': form, 'errors': form.errors})
    else:
        form = AnuForm()
        try:
            profile = Profile.objects.get(username=request.user)
        except:
            profile = {}
        return render(request, 'ftp/ProjectsPage/anu_apply.html', {'form': form, "prof": profile})


def view_anu_2022(request):
    # return HttpResponse('Hello ANU')
    if (request.method == "POST"):
        form = AnuForm_2022(request.POST or None, request.FILES or None)
        print(request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Applied successfully!')
            return redirect('ftp:anu_projects_confirmation')
        else:
            print(form.errors)
            return render(request, 'ftp/ProjectsPage/new_anu_apply.html', {'form': form, 'errors': form.errors})
    else:
        form = AnuForm_2022()
        return render(request, 'ftp/ProjectsPage/new_anu_apply.html', {'form': form})


def view_epfl_2022(request):
    # return HttpResponse('Hello ANU')
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        if (request.method == "POST"):
            form = EPFLForm_2022(request.POST or None, request.FILES or None)
            print(request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Applied successfully!')
                return redirect('ftp:epfl_projects_confirmation')
            else:
                print(form.errors)
                return render(request, 'ftp/ProjectsPage/epfl.html', {'form': form, 'errors': form.errors})
        else:
            try:
                profile = Profile.objects.get(username=request.user)
            except:
                profile = {}
            form = EPFLForm_2022()
            return render(request, 'ftp/ProjectsPage/epfl.html', {'form': form, 'prof': profile})


def saip_form(request):
    if (request.method == "POST"):
        form = SAIPForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Applied successfully!')
            return redirect('saip')
        else:
            print(form.errors)
            return render(request, 'ftp/ProjectsPage/saip.html', {'form': form, 'errors': form.errors})
    else:
        form = SAIPForm()
        # try:
        # 	profile = Profile.objects.get(username=request.user)
        # except:
        # 	profile = {}
        # return render(request, 'ftp/ProjectsPage/anu_apply.html', {'form':form, "prof": profile})
        return render(request, 'ftp/ProjectsPage/saip.html', {'form': form})


def view_scholarships(request):
    # return redirect('ftp:login_user')
    profile = None
    try:
        if request.user.is_authenticated:
            profile = Profile.objects.get(username=request.user)
    except Profile.DoesNotExist:
        pass

    appliedGKF = False
    status = []
    pendingNotifications = []

    if profile is not None:
        gkf_applis = gkf_appli.objects.filter(roll=profile.rollno)
        if len(gkf_applis):
            appliedGKF = True

    applications = []
    if profile is not None:
        applications = Application.objects.filter(profile=profile)

    if len(applications) > 0:
        for app in applications:
            status.append([app.project, app.status])

    if len(status) > 0:
        for s in status:
            statusId = s[0].id.urn[9:]
            if statusId + s[1] not in profile.viewedNotifications.split(','):
                pendingNotifications.append(s)
                profile.viewedNotifications = profile.viewedNotifications + \
                    statusId + s[1] + ','
                profile.save()

    if profile is not None:
        rem_scholarship = Scholarship.objects.exclude(
            id__in=[x.id for x in profile.scholarship.all()])
    else:
        rem_scholarship = Scholarship.objects.all()

    current_time = datetime.datetime.now().date()

    bookmarked = []
    if profile is not None:
        bookmarked = Project.objects.filter(bookmarks=profile)

    for proj in rem_scholarship:
        if current_time > proj.deadline:
            proj.display = False
            # print('qwerty')

    success = True

    for proj in rem_scholarship:
        if proj.display:
            success = False

    print(success)

    return render(request, 'ftp/Scholarship/scholarships.html',
                  {"success": success, 'allprojects': rem_scholarship, 'prof': profile, 'bookmarks': bookmarked, "pendingNotifications": pendingNotifications, "appliedGKF": appliedGKF})


def view_scholarships_new(request):
    # return redirect('ftp:login_user')
    profile = None
    try:
        if request.user.is_authenticated:
            profile = Profile.objects.get(username=request.user)
    except Profile.DoesNotExist:
        pass

    appliedGKF = False
    status = []
    pendingNotifications = []

    if profile is not None:
        gkf_applis = gkf_appli.objects.filter(roll=profile.rollno)
        if len(gkf_applis):
            appliedGKF = True

    applications = []
    if profile is not None:
        applications = Application.objects.filter(profile=profile)

    if len(applications) > 0:
        for app in applications:
            status.append([app.project, app.status])

    if len(status) > 0:
        for s in status:
            statusId = s[0].id.urn[9:]
            if statusId + s[1] not in profile.viewedNotifications.split(','):
                pendingNotifications.append(s)
                profile.viewedNotifications = profile.viewedNotifications + \
                    statusId + s[1] + ','
                profile.save()

    if profile is not None:
        rem_scholarship = Scholarship.objects.exclude(
            id__in=[x.id for x in profile.scholarship.all()])
    else:
        rem_scholarship = Scholarship.objects.all()

    current_time = datetime.datetime.now().date()

    bookmarked = []
    if profile is not None:
        bookmarked = Project.objects.filter(bookmarks=profile)

    for proj in rem_scholarship:
        if current_time > proj.deadline:
            proj.display = False
            # print('qwerty')

    success = True

    for proj in rem_scholarship:
        if proj.display:
            success = False

    print(success)

    return render(request, 'ftp/Scholarship/scholarships_new.html',
                  {"success": success, 'allprojects': rem_scholarship, 'prof': profile, 'bookmarks': bookmarked, "pendingNotifications": pendingNotifications, "appliedGKF": appliedGKF})


def view_scholarship_apply(request, scholarship_id):
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        try:
            scholarship = Scholarship.objects.get(id=scholarship_id)
            profile = Profile.objects.get(username=request.user)
            return render(request, 'ftp/Scholarship/apply_scholarship.html',
                          {'prof': profile, 'p': scholarship})
        except IndexError:
            return redirect('ftp:scholarships_new')


def yourscholarships(request):
    # return redirect('ftp:login_user')
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        try:
            profile = Profile.objects.get(username=request.user)
        except Profile.DoesNotExist:
            return redirect('ftp:create_profile')

        appliedGKF = False
        status = []
        pendingNotifications = []

        if profile is not None:
            gkf_applis = gkf_appli.objects.filter(roll=profile.rollno)
            if len(gkf_applis):
                appliedGKF = True

        applications = Application.objects.filter(profile=profile)
        for app in applications:
            status.append([app.project, app.status])

        for s in status:
            statusId = s[0].id.urn[9:]
            if statusId + s[1] not in profile.viewedNotifications.split(','):
                pendingNotifications.append(s)
                profile.viewedNotifications = profile.viewedNotifications + \
                    statusId + s[1] + ','
                profile.save()

        rem_scholarship = Scholarship_appli.objects.filter(profile=profile)

        # print(rem_scholarship[0])

        success = False
        if len(rem_scholarship) == 0:
            success = True

        for proj in rem_scholarship:
            if proj.display:
                success = False

        print(success)

        return render(request, 'ftp/Scholarship/applied_scholarship.html',
                      {"success": success, 'allprojects': rem_scholarship, 'prof': profile, "pendingNotifications": pendingNotifications, "appliedGKF": appliedGKF})


def apply(request, scholarship_id):
    return redirect('ftp:login_user')
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        profile = Profile.objects.get(username=request.user)
        return render(request, 'ftp/Scholarship/apply.html', {'prof': profile})


def apply_gkf(request):
    # return redirect('ftp:login_user')
    if (request.method == "POST"):
        form = GKFForm(request.POST or None, request.FILES or None)
        print(request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Applied successfully!')
            return redirect('ftp:gkf_confirmation')
        else:
            print(form.errors)
            return render(request, 'ftp/Scholarship/gkf.html', {'form': form, 'errors': form.errors})
    else:
        form = GKFForm()
        try:
            profile = Profile.objects.get(username=request.user)
        except:
            profile = {}
        return render(request, 'ftp/Scholarship/gkf.html', {'form': form, "prof": profile})


def apply_scholarships_2k23(request):
    if (request.method == "POST"):
        form = ScholarshipForm2k23(request.POST or None, request.FILES or None)
        print(request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Applied Successfully!')
            return redirect('ftp:scholarships_2k23_confirmation')
        else:
            print(form.errors)
            return render(request, 'ftp/Scholarship/scholarships2k23.html', {'form': form, 'errors': form.errors})
    else:
        form = ScholarshipForm2k23()
        try:
            profile = Profile.objects.get(username=request.user)
        except:
            profile = {}
        return render(request, 'ftp/Scholarship/scholarships2k23.html', {'form': form, "prof": profile})


def view_results(request):
    # return redirect('ftp:login_user')
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        try:
            profile = Profile.objects.get(username=request.user)
        except Profile.DoesNotExist:
            return redirect('ftp:create_profile')

        status = []
        pendingNotifications = []

        applications = Application.objects.filter(profile=profile)
        for app in applications:
            status.append([app.project, app.status])

        for s in status:
            statusId = s[0].id.urn[9:]
            if statusId + s[1] not in profile.viewedNotifications.split(','):
                pendingNotifications.append(s)
                profile.viewedNotifications = profile.viewedNotifications + \
                    statusId + s[1] + ','
                profile.save()

        res = Result.objects.all()
        return render(request, 'ftp/results/index.html', {'prof': profile, 'result': res, "pendingNotifications": pendingNotifications})


def already_applied(request):
    # return redirect('ftp:login_user')
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        try:
            profile = Profile.objects.get(username=request.user)
        except Profile.DoesNotExist:
            return redirect('ftp:create_profile')

        status = []
        pendingNotifications = []

        # applied_projects = profile.project.all()
        success = True
        applied_projects_app = Application.objects.filter(profile=profile)

        # applied_projects_app = [[x.project, x.sop, x.ncv] for x in applied_projects_app]
        applied_projects = []
        # application = []

        bookmarked = Project.objects.filter(bookmarks=profile)

        for app in applied_projects_app:
            success = False
            status.append([app.project, app.status])
            applied_projects.append([app.project, app.sop, app.ncv, app.project_domain1,
                                     app.project_domain2, app.project_domain3, app.Loi, app.status])

        for s in status:
            statusId = s[0].id.urn[9:]
            if statusId + s[1] not in profile.viewedNotifications.split(','):
                pendingNotifications.append(s)
                profile.viewedNotifications = profile.viewedNotifications + \
                    statusId + s[1] + ','
                profile.save()

        # for app in applied_projects_app:
        # application.append(app.sop)
        current_time = datetime.datetime.now().date()
        # STatus=Status.objects.filter(profile=profile)

        return render(request, 'ftp/ProjectsPage/yourapplications.html',
                      {'allprojects': applied_projects, 'prof': profile, "success": success, "bookmarks": bookmarked, 'date': current_time, 'ircstatus': applied_projects_app, "pendingNotifications": pendingNotifications})


def applied_students(request, project_id):
    user = request.user
    proj = get_object_or_404(Project, id=project_id)
    all_applied = Profile.objects.filter(
        application__project=proj, application__display_prof=True)
    success = False
    if len(all_applied) != 0:
        success = True
    if user.is_authenticated and user.is_irc:
        return render(request, 'ftp/profview/base.html', {'all_applied': all_applied, 'success': success, 'project': proj})
    elif user.is_authenticated and not user.is_irc:
        return HttpResponse("<h1>You don't have permission to view this page</h1>'")
    else:
        return render(request, 'ftp/profview/base.html', {'all_applied': all_applied, 'success': success, 'project': proj})


def view_frame(request, profile_id, project_id):
    all_applied = get_object_or_404(Profile, id=profile_id)
    proj_applied = get_object_or_404(Project, id=project_id)
    pro = get_object_or_404(
        Application, profile=all_applied, project=proj_applied)
    return render(request, 'ftp/profview/frame.html', {'all_applied': all_applied, 'pro': pro, 'project': proj_applied})

# def applied_students(request, project_id):
    # proj = get_object_or_404(Project, id=project_id)
    # all_applied = proj.profile.all()
    # success = False
    # success = True
    # if len(all_applied) != 0:
    # success = True

    # return render(request, 'ftp/profview/base.html') #, {'all_applied': all_applied, 'success': success, 'project': proj}


# def view_frame(request, profile_id, project_id):
    # all_applied = get_object_or_404(Profile, id=profile_id)
    # proj_applied = get_object_or_404(Project, id=project_id)
    # pro = get_object_or_404(Application, profile=all_applied, project=proj_applied)
    # return render(request, 'ftp/profview/frame.html') #, {'all_applied': all_applied, 'pro': pro, 'project': proj_applied}


def apply_project(request, project_id):
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        try:
            project = Project.objects.get(id=project_id)
            profile = Profile.objects.get(username=request.user)
            project_domain1 = request.POST.get('proj_domain1', None)
            project_domain2 = request.POST.get('proj_domain2', None)
            project_domain3 = request.POST.get('proj_domain3', None)
            ncv = request.FILES.get('ncv', None)
            noc = request.FILES.get('noc', None)
            sop = request.POST.get('sop', None)
            Loi = request.POST.get('Loi', None)

            if project.display:
                # print(Project.objects.filter(id=project_id)[0].university)
                Application.objects.create(profile=profile, project=project, project_domain1=project_domain1,
                                           project_domain2=project_domain2, project_domain3=project_domain3, sop=sop, ncv=ncv, Loi=Loi, noc=noc)
                messages.success(request, 'Applied successfully!')
                return redirect('ftp:projects')
            else:
                # logout(request)
                form = UserCreationForm(request.POST or None)
                context = {
                    "form": form,
                    "message": "You have been forcefully logged out.",
                }
                return render(request, 'ftp/login/login.html', context)

        except IndexError:
            # logout(request)
            form = UserCreationForm(request.POST or None)
            context = {
                "form": form,
                "message": "You have been forcefully logged out.",
            }
            return render(request, 'ftp/login/login.html', context)


def apply_finish(request, project_id):
    if not request.user.is_authenticated():
        return render(request, 'ftp/login/login.html')
    else:
        print(project_id)
        if request.method == "POST":
            form = ApplyForm(request.POST, request.FILES)
            print(form.errors)
            napp = form.save(commit=False)
            napp.user = request.user
            napp.project = Project.objects.filter(id=project_id)[0]
            # napp.profname = Projects.objects.filter(pk=project_id)[0].professor_name
            napp.profile = Profile.objects.filter(username=request.user.id)[0]
            napp.save()
            # print(napp.profname)

            # application = Applied.objects.filter(sop=request.POST['sop'])
            # print(1)
            # application.update(user=request.user.id)
            # print(2)
            # application.update(project=project_id)
            # print(3)
            # application.update(profile=Profile.objects.filter(username=request.user.id)[0].id)
            # print(4)
            # form.save()
            return redirect('/ftp/portal/projects/')


def apply_scholarship(request, scholarship_id):
    if request.method == 'POST':
        User = get_user_model()
        form = ScholarshipForm(request.POST or None, request.FILES or None)

        print('success1.05')
        print(scholarship_id)

        print(form.errors)
        if form.is_valid():
            print('jhbhjbjh')
            scholarship = get_object_or_404(Scholarship, id=scholarship_id)
            temp = form.save(commit=False)
            profile = None
            try:
                if request.user.is_authenticated:
                    profile = get_object_or_404(Profile, username=request.user)
                    temp.profile = profile
                    temp.Transcripts = profile.transcript
            except Profile.DoesNotExist:
                pass

            temp.scholarship = scholarship
            temp.save()
            messages.success(request, 'Applied successfully!')

            mail_subject = 'FTP: Your IITKGPF Application'

            if profile is None:
                message = render_to_string('ftp/scholarship_confirmation.html', {
                    'name': 'Student',
                })
            else:
                message = render_to_string('ftp/scholarship_confirmation.html', {
                    'name': profile.fullname,
                })

            email = None
            if request.user.is_authenticated:
                email = EmailMessage(
                    mail_subject, message, to=[request.user.email]
                )

            print(message)

            if email is not None:
                email.send(fail_silently=True)

            return redirect('ftp:scholarships_new')

        profile = None
        try:
            if request.user.is_authenticated:
                profile = Profile.objects.get(username=request.user)
        except Profile.DoesNotExist:
            pass

        context = {"form": form, 'errors': form.errors, 'prof': profile}
        return render(request, 'ftp/Scholarship/apply_scholarship.html', context)
    else:
        print("sucess1.02")
        form = ScholarshipForm()
        profile = None
        if request.user.is_authenticated:
            profile = get_object_or_404(Profile, username=request.user)
        context = {"form": form, 'prof': profile}
        return render(request, 'ftp/Scholarship/apply_scholarship.html', context)

# def notifications(request):
# 	if not request.user.is_authenticated:
# 		return redirect('ftp:login_user')
# 	else:
# 		try:
# 			profile = Profile.objects.get(username=request.user)
# 			results = Result.objects.all()

# 			success = True
# 			if not results:
# 				success = False

# 			return render(request, 'ftp/ProjectsPage/notifications.html', {'success': success, 'results': results, 'prof': profile})

# 		except Profile.DoesNotExist:
# 			return redirect('ftp:create_profile')


# def apply_scholarships(request, scholarship_id):
# if not request.user.is_authenticated():
# return render(request, 'login.html')
# else:
# print(scholarship_id)
# project = Scholarship.objects.filter(pk=scholarship_id)[0]
# if project.display:
# print(Scholarship.objects.filter(pk=scholarship_id)[0].funding_agency)
# return render(request, 'scholarshipdetail.html', {'project': project})
# else:
# logout(request)
# form = UserCreationForm(request.POST or None)
# context = {
# "form": form,
# "message": "You have been forcefully logged out.",
# }
# return render(request, 'login.html', context)
#
#
# def apply_finish_scholarships(request,  scholarship_id):
# if not request.user.is_authenticated():
# return render(request, 'login.html')
# else:
# print(scholarship_id)
# if request.method == "POST":
# form = ApplyScholarshipForm(request.POST, request.FILES)
# print(form.errors)
# napp = form.save(commit=False)
# napp.user = request.user
# napp.scholarship = Scholarship.objects.filter(pk=scholarship_id)[0]
# # napp.profname = Projects.objects.filter(pk=project_id)[0].professor_name
# napp.profile = Profile.objects.filter(username=request.user.id)[0]
# # napp.funding_agency = Scholarship.objects.filter(pk=project_id)[0].funding_agency
# napp.save()
# # print(napp.profname)
#
# # application = Applied.objects.filter(sop=request.POST['sop'])
# # print(1)
# # application.update(user=request.user.id)
# # print(2)
# # application.update(project=project_id)
# # print(3)
# # application.update(profile=Profile.objects.filter(username=request.user.id)[0].id)
# # print(4)
# # form.save()
# return redirect('/ftp/portal/scholarships/')


def forgotpass(request):
    User = get_user_model()
    print("Not Post")
    if request.method == 'POST':
        username = str(request.POST.get('username')).lower()
        if ('@iitkgp.ac.in' in username) or ("@kgpian.iitkgp.ac.in" in username):
            username = username.split("@")[0]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, 'ftp/login/forgot_password_form.html', {'error': 'No user found with username: '+username})
        print(account_activation_token.make_token(user))
        print("yes")
        current_site = get_current_site(request)
        mail_subject = 'FTP: Password Reset'
        message = render_to_string('ftp/login/password_reset_activation.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': forgot_password_token.make_token(user),
        })
        email = EmailMessage(
            mail_subject, message, settings.EMAIL_HOST_USER, to=[user.email]
        )
        print(message)
        email.send(fail_silently=True)
        print("email sent")
        return render(request, 'ftp/login/Reset_Email_sent.html', context={'email': user.email})
    else:
        return render(request, 'ftp/login/forgot_password_form.html')


def pass_reset(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and forgot_password_token.check_token(user, token):
        username = user.username
        return render(request, 'ftp/login/password_reset_form.html', {'username': username})
    else:
        return HttpResponse('Password reset link is either invalid or you already changed your password using this link. Try creating it <a href="/ftp/forgot-send_email/">here</a> again')


def pass_reset_done(request):
    User = get_user_model()
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            user = User.objects.get(username=username)
            user.set_password(password1)
            user.save()
            return redirect('ftp:login_user')
        else:
            return render(request, 'ftp/login/password_reset_form.html',
                          {'username': username, 'error': "The passwords do not match."})


def edit_profile(request):
    print("User enter edit function")
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')

    try:
        profile = Profile.objects.get(username=request.user)
    except Profile.DoesNotExist:
        return redirect('ftp:create_profile')

    status = []
    pendingNotifications = []

    applications = Application.objects.filter(profile=profile)
    for app in applications:
        status.append([app.project, app.status])

    for s in status:
        statusId = s[0].id.urn[9:]
        if statusId + s[1] not in profile.viewedNotifications.split(','):
            pendingNotifications.append(s)
            profile.viewedNotifications = profile.viewedNotifications + \
                statusId + s[1] + ','
            profile.save()

    if request.method == 'POST':
        print("POSTED USER")
        fs = FileSystemStorage()
        print(profile.fullname)
        photo = request.FILES.get('photo', None)
        passport = request.POST.get('passport', None)
        cgpa = request.POST.get('cgpa', None)
        cv = request.FILES.get('cv', None)
        transcript = request.FILES.get('transcript', None)
        print(transcript)
        contact = request.POST.get('contact', None)
        alt_email = request.POST.get('alt_email', None)
        print(cv, cgpa, alt_email)

        if photo:
            print("entered photo")
            ext = os.path.splitext(photo.name)[1]
            pathname = request.user.username + "_p" + upload_time() + ext
            fs.save(pathname, photo)
            # if profile.photo.name:
            # 	 fs.delete(profile.photo.name)
            profile.photo.name = pathname

        if passport:
            profile.passport = passport

        if cgpa:
            profile.cgpa = cgpa

        if cv:
            ext = os.path.splitext(cv.name)[1]
            pathname = request.user.username + "_c" + upload_time() + ext
            fs.save(pathname, cv)
            # fs.delete(profile.cv.name)
            profile.cv.name = pathname
            profile.updated = True
            print("updated")

        if contact:
            print('entered contact', contact)
            profile.contact = contact

        if alt_email:
            profile.alt_email = alt_email

        if transcript:
            # if request.user.username not in profile.transcript.name:
            ext = os.path.splitext(transcript.name)[1]
            pathname = request.user.username + "_t" + upload_time() + ext
            fs.save(pathname, transcript)
            # fs.delete(profile.transcript.name)
            profile.transcript.name = pathname
            profile.updated = True
            print("updated")
            # else:
            # profile.save()
            # print("Transcript problem")
            # return render(request, 'ftp/profile/edit_profile.html', {'profile': profile,
            # 'errors': "Transcript update failed. Transcript can be updated only after five days of its last update."})

        profile.save()
        print("Profile save edited")
        return redirect('ftp:projects')
    else:
        return render(request, 'ftp/profile/edit_profile.html', {'prof': profile, "profile": profile, "pendingNotifications": pendingNotifications})


def upload_time():
    import datetime
    time = datetime.datetime.now()
    s = time.strftime("%d%m%y%H%M%S")
    return str(s)


def upload_date():
    import datetime
    time = datetime.datetime.now()
    s = time.strftime("%d%m%y")
    return str(s)


def save_profile(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    else:
        if request.method == "POST":
            photo = request.FILES.get('photo', None)
            passport = request.POST.get('passport', None)
            cgpa = request.POST.get('cgpa', None)
            cv = request.FILES.get('cv', None)
            transcript = request.FILES.get('transcript', None)
            contact = request.POST.get('contact', None)
            alt_email = request.POST.get('alt_email', None)

            print(contact, passport, cgpa, alt_email)

            fs = FileSystemStorage()
            profile = Profile.objects.get(username=request.user)

            if photo:
                ext = os.path.splitext(photo.name)[1]
                pathname = request.user.username + "_p" + upload_time() + ext
                fs.save(pathname, photo)
                fs.delete(profile.photo.name)
                profile.photo.name = pathname

            if passport:
                profile.passport = passport

            if cgpa:
                profile.cgpa = cgpa

            if cv:
                ext = os.path.splitext(cv.name)[1]
                pathname = request.user.username + "_c" + upload_time() + ext
                fs.save(pathname, cv)
                fs.delete(profile.cv.name)
                profile.cv.name = pathname

            if contact:
                profile.contact = contact

            if alt_email:
                profile.alt_email = alt_email

            if transcript:
                if request.user.username not in profile.transcript.name:
                    ext = os.path.splitext(transcript.name)[1]
                    pathname = request.user.username + "_t" + upload_date() + ext
                    fs.save(pathname, transcript)
                    fs.delete(profile.transcript.name)
                    profile.transcript.name = pathname
                else:
                    profile.save()
                    return render(request, 'ftp/profile/edit_profile.html', {'profile': profile,
                                                                             'error': "Transcript update failed. Transcript can be updated only after five days of its last update."})

            profile.save()

            print(profile.fullname)

            return redirect('/ftp/portal/projects/')


# def results(request):
# if not request.user.is_authenticated():
# return render(request, 'login.html')
# else:
# allresults = Results.objects.all()
# return render(request, 'results.html', {'allresults': allresults})
#
#
# def scholarshipresults(request):
# if not request.user.is_authenticated():
# return render(request, 'login.html')
# else:
# allresults = ScholarshipResults.objects.all()
# return render(request, 'scholarshipresults.html', {'allresults': allresults})
#


def edit_application(request):
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        profile = Profile.objects.filter(username=request.user)
        if len(Profile.objects.filter(username=request.user.id)) == 1:
            return redirect('ftp:projects')
        else:
            if request.method == "POST":
                print('lsdv')
                ncv = request.FILES.get('ncv', None)
                sop = request.POST.get('sop', None)
                app = Application.objects.get(profile=profile)
                app.ncv = ncv
                app.sop = sop
                app.save()
            else:
                return render(request, 'ftp/edit_app.html', {'profile': profile})


def view_favorite(request):
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        profile = Profile.objects.get(username=request.user)
        if profile is None:
            return redirect('ftp:create_profile')
        else:
            status = []
            pendingNotifications = []

            applications = Application.objects.filter(profile=profile)
            for app in applications:
                status.append([app.project, app.status])

            for s in status:
                statusId = s[0].id.urn[9:]
                if statusId + s[1] not in profile.viewedNotifications.split(','):
                    pendingNotifications.append(s)
                    profile.viewedNotifications = profile.viewedNotifications + \
                        statusId + s[1] + ','
                    profile.save()

            bookmarked = Project.objects.filter(bookmarks=profile)
            success = True
            proj_domains = ProjectDomain.objects.all()

            for e in bookmarked:
                success = False
                break

            applied_projects_app = Application.objects.filter(profile=profile)
            applied_projects = []
            for app in applied_projects_app:
                applied_projects.append(app.project)
            current_time = datetime.datetime.now().date()
            return render(request, 'ftp/ProjectsPage/bookmarks.html',
                          {"success": success, 'allprojects': bookmarked, 'prof': profile, 'applieds': applied_projects, 'proj_domains': proj_domains, 'app': applied_projects_app, 'date': current_time, 'selected': profile.selected, 'pendingNotifications': pendingNotifications})


def add_favorite(request, pk):
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        data = {'fb': False}
        project_id = pk
        try:
            project = Project.objects.get(id=project_id)
            profile = Profile.objects.get(username=request.user)

            all_bookmarks = Project.objects.filter(bookmarks=profile)
            if project not in all_bookmarks:
                project.bookmarks.add(profile)
            else:
                project.bookmarks.remove(profile)

            data = {'fb': True}
            return redirect('/ftp/projects')
        except IndexError:
            return JsonResponse(data)


def get_detail(request):
    form = ProfForm(request.POST or None)
    if form.is_valid():
        print(form.errors)
        # form.save(commit=False).username = request.user.id
        make_prof = form.save(commit=False)

        # project=Project()
        # print(project,make_prof)
        # project.project_name=make_prof.project_name
        # project.professor_name=make_prof.name
        # project.project_detail=make_prof.project_details
        # project.project_time=make_prof.duration
        # project.university=make_prof.university_name
        # project.save()
        # print (project)

        make_prof.save()
        # prof = Profile.objects.filter(fullname=request.POST['fullname'])
        print(make_prof)

        return render(request, 'ftp/prof_success.html')
    else:
        print(form.errors)
        return render(request, 'ftp/prof_form.html', {'form': form})


def view_profile(request):
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        try:
            profile = Profile.objects.get(username=request.user)
        except Profile.DoesNotExist:
            return redirect('ftp:create_profile')

        status = []
        pendingNotifications = []

        applications = Application.objects.filter(profile=profile)
        for app in applications:
            status.append([app.project, app.status])

        for s in status:
            statusId = s[0].id.urn[9:]
            if statusId + s[1] not in profile.viewedNotifications.split(','):
                pendingNotifications.append(s)
                profile.viewedNotifications = profile.viewedNotifications + \
                    statusId + s[1] + ','
                profile.save()

        return render(request, 'ftp/profile/view_profile.html', {"prof": profile, "pendingNotifications": pendingNotifications})


# def dyuti(request):
# form = DyutiForm(request.POST or None)
# if form.is_valid():
# tp = form.save(commit=False)
# cours = request.POST.getlist('course')
#

def dashboard_mail(request):
    user = request.user
    if user.is_irc:
        if request.method == 'POST':
            mails_sent = 0
            # print("Helloooooooooooo anjasnjsancasjcsakcsac svds kjnsdkvjsdvsdkjvnsdkjnscXXXXXXXXXXXXXXXXXX HELOO LOOOLOL")
            error_message = "No Errors"
            typeofmail = request.POST['finaltype']
            print(typeofmail)
            message1 = request.POST['message1']
            message2 = request.POST['message2']
            message3 = request.POST['message3']
            message4 = request.POST['message4']
            if (typeofmail == "1"):
                message = message1
            elif (typeofmail == "2"):
                message = message2
            elif (typeofmail == "3"):
                message = message3
            else:
                message = message4
            email = request.POST['finalemail']
            alt_email = request.POST['finalaltemail']
            subject = 'FTP: Important Notice'
            # print(type(message))
            print(message)
            print(email)
            # message = "Hellooooooooooooooooo Supppppppppppp"
            print(message)
            print(alt_email)
            # email = EmailMessage(
            # 				subject, message, settings.EMAIL_HOST_USER, to=[email]
            # 			)
            # email.send(fail_silently=True)
            try:
                email2 = EmailMultiAlternatives(
                    subject, message, settings.EMAIL_HOST_USER, to=[
                        email, alt_email]
                )
            except:
                email2 = EmailMultiAlternatives(
                    subject, message, settings.EMAIL_HOST_USER, to=[
                        email, alt_email]
                )
            email2.attach_alternative(message, "text/html")
            if typeofmail == "2":
                email2.attach_file(os.path.join(
                    settings.BASE_DIR, 'media/Undertaking.pdf'))
            try:
                email2.send(fail_silently=True)
                mails_sent += 1
            except Exception as e:
                error_message = str(e.args) + "For recipient: " + email
            log = "[" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Sending_new_project_email | " + email + \
                " | " + str(mails_sent) + " mails sent | " + \
                error_message + "</br>"
            # logfile = open(os.path.join(settings.BASE_DIR, 'templates/logs/dashboard_log.html'), "a")
            # logfile = open("logs/dashboard_log.html", "a")
            # logfile.write(log)
            # logfile.close()
            if error_message != "No Errors":
                messages.success(
                    request, 'All email were not sent successfully. Check logs.')
            else:
                messages.success(request, 'Email sent successfully!')
    else:
        raise Http404('Page does not Exist')

    projects = Project.objects.all()
    # Searching for projects
    if request.GET.get('search'):
        search = request.GET.get('search')
        projects = Project.objects.filter(Q(project_name__icontains=search) | Q(
            professor_name__icontains=search) | Q(university__icontains=search))
    profile = get_object_or_404(Profile, username=request.user)
    display = []
    display_past = []
    professors = Professor.objects.all()
    for project in projects:
        applications = Application.objects.filter(project=project)
        # If deadline is crossed
        if project.deadline < datetime.date.today():
            display_past.append([project, applications])
        else:
            display.append([project, applications])
    # Sorting the searched projects
    display.sort(reverse=True, key=lambda x: x[0].deadline)
    display_past.sort(reverse=True, key=lambda x: x[0].deadline)
    if request.GET.get('sort'):
        sort = request.GET.get('sort')
        if sort == 'project_name':
            display.sort(key=lambda x: x[0].project_name.lower())
            display_past.sort(key=lambda x: x[0].project_name.lower())
        if sort == 'professor_name':
            display.sort(key=lambda x: x[0].professor_name.lower())
            display_past.sort(key=lambda x: x[0].professor_name.lower())
        if sort == 'date':
            display.sort(reverse=True, key=lambda x: x[0].deadline)
            display_past.sort(reverse=True, key=lambda x: x[0].deadline)
    # Stop showing add result button for these projects
    projects_declared = []
    results = Result.objects.all()
    for result in results:
        projects_declared.append(result.project)
    print(projects_declared)
    return render(request, 'ftp/admin/projects2023.html', {'displaylist': display, 'displaylist_past': display_past, 'allprofessors': professors, 'prof': profile, 'projects_declared': projects_declared})
    # return redirect('ftp:admin_projects')


def admin_projects(request):
    user = request.user
    try:
        is_irc = user.is_irc
    except:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")
    if user.is_irc:
        '''
        # Deleting application
        if request.GET.get('aid'):
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        aid = request.GET.get(
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            'aid')
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        Application.objects.filter(
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            id=aid).delete()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        messages.success(
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            request, 'Application deleted successfully!')
        '''
        # Sending Emails New
        # if request.GET.get('pnameformail'):
        # 	pname2 = request.GET.get('pnameformail')

        # Sending Emails
        if request.GET.get('pname'):
            pname = request.GET.get('pname')
            project = Project.objects.get(project_name=pname)
            users = CustomUser.objects.all()
            mails_sent = 0
            error_message = "No Errors"
            for each_user in users:
                try:
                    name = Profile.objects.get(username=each_user).fullname
                except:
                    name = each_user.username
                subject = 'FTP: New Project Added'
                message = render_to_string('ftp/new_project_email.html', {
                    'project': project,
                    'name': name,
                })
                print(message)
                try:
                    alt_email = Profile.objects.filter(
                        username=each_user).alt_email
                    email = EmailMessage(
                        subject, message, settings.EMAIL_HOST_USER, to=[], bcc=[each_user.email, alt_email]
                    )
                except:
                    email = EmailMessage(
                        subject, message, settings.EMAIL_HOST_USER, to=[], bcc=[each_user.email]
                    )
                try:
                    email.send(fail_silently=True)
                    mails_sent += 1
                except Exception as e:
                    error_message = str(e.args) + "For recipient: " + email
                    break
            log = "[" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Sending_new_project_email | " + user.username + \
                " | " + str(mails_sent) + " mails sent | " + \
                error_message + "</br>"
            # logfile = open(os.path.join(settings.BASE_DIR, 'templates/logs/dashboard_log.html'), "a")
            # logfile.write(log)
            # logfile.close()
            if error_message != "No Errors":
                messages.success(
                    request, 'All emails were not sent successfully. Check logs.')
            else:
                messages.success(request, 'Emails sent successfully!')

        projects = Project.objects.all()
        # Searching for projects
        if request.GET.get('search'):
            search = request.GET.get('search')
            projects = Project.objects.filter(Q(project_name__icontains=search) | Q(
                professor_name__icontains=search) | Q(university__icontains=search))
        profile = get_object_or_404(Profile, username=request.user)
        display = []
        display_past = []
        professors = Professor.objects.all()
        for project in projects:
            applications = Application.objects.filter(project=project)
            # If deadline is crossed
            if project.deadline < datetime.date.today():
                display_past.append([project, applications])
            else:
                display.append([project, applications])

        project_tag = ProjectTag.objects.all()

        # Sorting the searched projects
        display.sort(reverse=True, key=lambda x: x[0].deadline)
        display_past.sort(reverse=True, key=lambda x: x[0].deadline)
        if request.GET.get('sort'):
            sort = request.GET.get('sort')
            if sort == 'project_name':
                display.sort(key=lambda x: x[0].project_name.lower())
                display_past.sort(key=lambda x: x[0].project_name.lower())
            if sort == 'professor_name':
                display.sort(key=lambda x: x[0].professor_name.lower())
                display_past.sort(key=lambda x: x[0].professor_name.lower())
            if sort == 'date':
                display.sort(reverse=True, key=lambda x: x[0].deadline)
                display_past.sort(reverse=True, key=lambda x: x[0].deadline)
        # Stop showing add result button for these projects
        projects_declared = []
        results = Result.objects.all()
        for result in results:
            projects_declared.append(result.project)
        print(projects_declared)
        return render(request, 'ftp/admin/projects2023.html', {'displaylist': display, 'displaylist_past': display_past, 'allprofessors': professors, 'prof': profile, 'projects_declared': projects_declared, 'projtag': project_tag})
    else:
        raise Http404('Page does not Exist')


def deletetags(request, pk):
    pro_tag = get_object_or_404(ProjectTag, id=pk)
    pro_tag.delete()
    return redirect("ftp:admin_project_tag")


def applicant_mail(request):
    user = request.user
    try:
        is_irc = user.is_irc
    except:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")
    if user.is_irc:
        aid = request.GET.get('aid')
        application = Application.objects.filter(id=aid)[0]
        project = application.project
        all_applied = project.profile.all()
        profile = application.profile
        applicants = Application.objects.filter(project=project)
        # return render(request, 'ftp/admin/applicant_profile/profile_frame.html', {'application': application, 'profile': profile, 'applicants': applicants})
        return render(request, 'ftp/admin/applicant_profile/dash_mail_new4.html', {'application': application, 'profile': profile, 'applicants': applicants, 'project': project})
    return HttpResponse("<h1>You don't have permission to view this page</h1>")


def applicant_profile(request):
    user = request.user
    try:
        is_irc = user.is_irc
    except:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")
    if user.is_irc:
        aid = request.GET.get('aid')
        application = Application.objects.filter(id=aid)[0]
        project = application.project
        all_applied = project.profile.all()
        profile = application.profile
        applicants = Application.objects.filter(project=project)
        return render(request, 'ftp/admin/applicant_profile/profile_frame.html', {'application': application, 'profile': profile, 'applicants': applicants})
    return HttpResponse("<h1>You don't have permission to view this page</h1>")


class applicant_profile_edit(UpdateView):
    model = Application
    template_name = 'ftp/admin/appli_profile_edit.html'
    fields = ['sop', 'ncv']
    success_url = reverse_lazy('ftp:admin_projects')


def admin_scholarship(request):
    user = request.user
    try:
        is_irc = user.is_irc
    except:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")
    if user.is_irc:
        scholarship = Scholarship.objects.all()
        gkf = gkf_appli.objects.all()
        profile = get_object_or_404(Profile, username=request.user)
        info = []
        for scho in scholarship:
            application = Scholarship_appli.objects.filter(scholarship=scho)
            info.append([scho, application])

        return render(request, 'ftp/admin/scholarship.html', {'scholarship': info, 'gkf': gkf})
    else:
        raise Http404('Page does not Exist')


def scholarship_applicant_profile(request):
    user = request.user
    try:
        is_irc = user.is_irc
    except:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")
    if user.is_irc:
        aid = request.GET.get('aid')
        application = Scholarship_appli.objects.filter(id=aid)[0]
        scholarship = application.scholarship
        all_applied = scholarship.profile.all()
        profile = application.profile
        applicants = Scholarship_appli.objects.filter(scholarship=scholarship)
        return render(request, 'ftp/admin/applicant_profile/scholarship_profile_frame.html', {'application': application, 'profile': profile, 'applicants': applicants})
    return HttpResponse("<h1>You don't have permission to view this page</h1>")


def gkf_scholarship_applicant_profile(request):
    user = request.user
    try:
        is_irc = user.is_irc
    except:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")
    if user.is_irc:
        aid = request.GET.get('aid')
        application = gkf_appli.objects.filter(id=aid)[0]
        applicants = gkf_appli.objects.all()
        return render(request, 'ftp/admin/applicant_profile/gkf_scholarship_profile_frame.html', {'application': application, 'profile': application, 'applicants': applicants})
    return HttpResponse("<h1>You don't have permission to view this page</h1>")


def admin_profiles(request):
    user = request.user
    try:
        is_irc = user.is_irc
    except:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")
    if user.is_irc:
        profiles = Profile.objects.all()
        profile = get_object_or_404(Profile, username=request.user)
        # print(profiles)
        # Converting query set object into list
        profiles = [i for i in profiles]
        profiles.sort(key=lambda x: x.fullname.lower())
        if request.GET.get('sort'):
            sort = request.GET.get('sort')
            if sort == 'fullname':
                profiles.sort(key=lambda x: x.fullname.lower())
            if sort == 'rollno':
                profiles.sort(reverse=True, key=lambda x: x.rollno)
            if sort == 'department':
                profiles.sort(key=lambda x: x.department.lower())
        return render(request, 'ftp/admin/profiles.html', {'allprofiles': profiles, 'prof': profile})
    else:
        raise Http404('Page does not Exist')


def export_profile(request):
    if request.user.is_irc:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Profile List.csv"'
        writer = csv.writer(response)
        writer.writerow(['username', 'fullname', 'department', 'contact', 'year',
                         'email', 'alt_email', 'passport', 'degree_type', 'cgpa', 'rollno', 'alt_email', 'selected'])
        profile = Profile.objects.all().values_list('username', 'fullname', 'department',
                                                    'contact', 'year', 'alt_email', 'passport', 'degree_type', 'cgpa', 'rollno', 'alt_email', 'selected')
        for each_profile in profile:
            writer.writerow(each_profile)
        return response
    else:
        raise Http404('Page does not Exist')


def export_scholarships(request):
    if request.user.is_irc:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Scholarships.csv"'
        scholarships = scholarship2k23_appli.objects.all()
        writer = csv.writer(response)
        writer.writerow(['Name', 'Roll', 'Email', 'Year', 'CGPA', 'Transcript', 'Backlog', 'Applying For', 'Offer Letter',
                        'Host University', 'Mode', 'From', 'To', 'NOC', 'LOR', 'Previously Funded', 'Funding Proof', 'Project Desc'])
        scholarships = scholarship2k23_appli.objects.all().values_list('name', 'roll', 'email', 'yearOfStudy', 'cgpa', 'transcript', 'hasBacklog', 'applying_to',
                                                                       'offer_letter', 'hostUniversity', 'mode', 'durationOfVisit_from', 'durationOfVisit_to', 'noc', 'lor', 'previously_funded', 'funding_proof', 'project_desc')
        for each_scholarship in scholarships:
            writer.writerow(each_scholarship)
        return response
    else:
        raise Http404('Page does not exist')


def export_emails(request):
    if request.user.is_irc:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Emails.csv"'
        users = Profile.objects.all()
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email'])
        users = Profile.objects.all().values_list('fullname', 'alt_email')
        for user in users:
            writer.writerow(user)
        return response
    else:
        raise Http404('Page does not exist')


def export_topics(request):
    if request.user.is_irc:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Topicslist.csv"'
        writer = csv.writer(response)
        writer.writerow(['TopicName', 'count', 'verified'])
        topics = RequestedTopic.objects.all().values_list(
            'topicName', 'count', 'verified')
        for each_topic in topics:
            writer.writerow(each_topic)
        return response
    else:
        raise Http404('Page does not Exist')


def export_mail_ids(request):
    if request.user.is_irc:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Mail List.csv"'
        writer = csv.writer(response)
        writer.writerow(['fullname', 'email'])
        profile = Profile.objects.all().values_list(
            'fullname', 'alt_email', 'username_id')
        for each_profile in profile:
            user = CustomUser.objects.get(id=each_profile[2])
            writer.writerow((each_profile[0], user.email))
            writer.writerow((each_profile[0], each_profile[1]))
        return response
    else:
        raise Http404('Page does not Exist')


def export_professor(request):
    if request.user.is_irc:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Professor List.csv"'
        writer = csv.writer(response)
        writer.writerow(['name', 'university_name', 'project_name', 'skype'])
        profile = Professor.objects.all().values_list(
            'name', 'university_name', 'project_name', 'skype')
        for each_profile in profile:
            writer.writerow(each_profile)
        return response
    else:
        raise Http404('Page does not Exist')


def export_saip(request):
    if request.user.is_irc:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="SAIP List.csv"'
        writer = csv.writer(response)
        writer.writerow(['name', 'rollno', 'email', 'query', 'mode_of_saip'])
        profile = SAIP.objects.all().values_list(
            'fullname', 'rollno', 'email', 'query', 'mode_of_saip')
        for each_profile in profile:
            writer.writerow(each_profile)
        return response
    else:
        raise Http404('Page does not Exist')


def export_hult(request):
    if request.user.is_irc:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Hult List.csv"'
        writer = csv.writer(response)
        writer.writerow(['team_name', 'email_leader', 'member_2', 'email_mem2',
                         'member_3', 'email_mem3', 'member_4', 'email_mem4', 'queries'])
        hult = Hult.objects.all().values_list('team_name', 'email_leader', 'member_2',
                                              'email_mem2', 'member_3', 'email_mem3', 'member_4', 'email_mem4', 'queries')
        for each_hult in hult:
            writer.writerow(each_hult)
        return response
    else:
        raise Http404('Page does not Exist')


def export_dyuti(request):
    if request.user.is_irc:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Dyuti List.csv"'
        writer = csv.writer(response)
        writer.writerow(['first_name', 'last_name', 'phone', 'email', 'gender', 'country', 'passport_no', 'visa_no', 'visa_cate',
                         'visa_validity', 'uni_india', 'state', 'city', 'department', 'year_of_study', 'reg_no', 'is_scholarship'])
        dyuti = Dyuti.objects.all().values_list('first_name', 'last_name', 'phone', 'email', 'gender', 'country', 'passport_no', 'visa_no',
                                                'visa_cate', 'visa_validity', 'uni_india', 'state', 'city', 'department', 'year_of_study', 'reg_no', 'is_scholarship')
        for each_dyuti in dyuti:
            writer.writerow(each_dyuti)
        return response
    else:
        raise Http404('Page does not Exist')


def export_applied_list(request, pk):
    if request.user.is_irc:
        project = Project.objects.get(pk=pk)
        query_set = project.application_set.all()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=" ' + \
            project.project_name + ' List.csv"'
        writer = csv.writer(response)
        writer.writerow(['Username', 'Fullname', 'Roll No', 'Contact No', 'CGPA',
                         'Department', 'CV', 'TRANSCRIPT', 'SOP', 'Letter of Importance'])

        for each in query_set:
            if each.ncv:
                writer.writerow([each.profile.username, each.profile.fullname, each.profile.rollno, each.profile.contact, each.profile.cgpa, each.profile.department,
                                 'https://ircell.iitkgp.ac.in' + each.ncv.url, 'https://ircell.iitkgp.ac.in' + each.profile.transcript.url, each.sop, each.Loi])
            else:
                writer.writerow([each.profile.username, each.profile.fullname, each.profile.rollno, each.profile.contact, each.profile.cgpa, each.profile.department,
                                 'https://ircell.iitkgp.ac.in' + each.profile.cv.url, 'https://ircell.iitkgp.ac.in' + each.profile.transcript.url, each.sop, each.Loi])
        return response
    else:
        raise Http404('Page does not Exist')


def export_gkf(request):
    if request.user.is_irc:
        query_set = gkf_appli.objects.all()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=" GKF List.csv"'
        writer = csv.writer(response)
        writer.writerow(['Full Name', 'Roll No', 'Email', 'Contact', 'Student', 'Year of Study', 'Department', 'CGPA', 'Transcript',
                         'CV', 'SOP', 'Type', 'Offer Letter', 'NOC', 'From', 'To', 'Host University', 'Previously Funded', 'Funding Proof'])

        for each in query_set:
            if each.funding_proof:
                writer.writerow([each.name, each.roll, each.email, each.contact, each.student, each.yearOfStudy, each.department, each.cgpa,  'https://ircell.iitkgp.ac.in' + each.transcript.url, 'https://ircell.iitkgp.ac.in' + each.cv.url, each.sop, each.type,
                                 'https://ircell.iitkgp.ac.in' + each.offer_letter.url, 'https://ircell.iitkgp.ac.in' + each.noc.url, 'D: ' + each.durationOfVisit_from, 'D: ' + each.durationOfVisit_to, each.hostUniversity, each.previously_funded, 'https://ircell.iitkgp.ac.in' + each.funding_proof.url])
            else:
                writer.writerow([each.name, each.roll, each.email, each.contact, each.student, each.yearOfStudy, each.department, each.cgpa,  'https://ircell.iitkgp.ac.in' + each.transcript.url, 'https://ircell.iitkgp.ac.in' + each.cv.url, each.sop, each.type,
                                 'https://ircell.iitkgp.ac.in' + each.offer_letter.url, 'https://ircell.iitkgp.ac.in' + each.noc.url, 'D: ' + each.durationOfVisit_from, 'D: ' + each.durationOfVisit_to, each.hostUniversity, each.previously_funded, "Not Funded!"])
        return response
    else:
        raise Http404('Page does not Exist')


def export_applied_anu_list(request, project_name):
    if request.user.is_irc:
        query_set = Anu.objects.filter(Q(pref1=project_name) | Q(
            pref2=project_name) | Q(pref3=project_name))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=" ' + \
            project_name + ' List.csv"'
        writer = csv.writer(response)
        writer.writerow(['Fullname', 'Roll No', 'Email', 'Year of Study', 'Contact No',
                         'Statement of Purpose', 'Is former FRT Award Recepient?', 'Letter of Recommendation (1)', 'Letter of Recommendation (2)', 'Latest CV', 'Undertaking', 'Transcript', 'Project pref 1', 'Project pref 2', 'Project pref 3'])

        for each in query_set:
            writer.writerow([each.fullname, each.rollno, each.email, each.year, each.contact, each.sop, each.former_anu, 'https://ircell.iitkgp.ac.in' + each.lor1.url, 'https://ircell.iitkgp.ac.in' + each.lor2.url,
                             'https://ircell.iitkgp.ac.in' + each.undertaking.url, 'https://ircell.iitkgp.ac.in' + each.cv.url, 'https://ircell.iitkgp.ac.in' + each.transcript.url, each.pref1, each.pref2, each.pref3])
        return response
    else:
        raise Http404('Page does not Exist')


def export_applied_anu_all_list(request):
    if request.user.is_irc:
        query_set = Anu.objects.all()

        print(query_set)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=ANU_applicants_list.csv'
        writer = csv.writer(response)
        writer.writerow(['Fullname', 'Roll No', 'Email', 'Year of Study', 'Contact No',
                         'Statement of Purpose', 'Is former FRT Award Recepient?', 'Letter of Recommendation (1)', 'Letter of Recommendation (2)', 'Latest CV', 'Undertaking', 'Transcript', 'Project pref 1', 'Project pref 2', 'Project pref 3'])

        for each in query_set:
            writer.writerow([each.fullname, each.rollno, each.email, each.year, each.contact, each.sop, each.former_anu, 'https://ircell.iitkgp.ac.in' + each.lor1.url, 'https://ircell.iitkgp.ac.in' + each.lor2.url,
                             'https://ircell.iitkgp.ac.in' + each.undertaking.url, 'https://ircell.iitkgp.ac.in' + each.cv.url, 'https://ircell.iitkgp.ac.in' + each.transcript.url, each.pref1, each.pref2, each.pref3])
        return response
    else:
        raise Http404('Page does not Exist')


def project_create(request):
    user = request.user
    if user.is_irc:
        # form = ProjectForm(request.POST or None)
        form = ProjectForm(request.POST, request.FILES)
        try:
            prereq = PreRequisite.objects.get(
                detail=request.POST.get('prereq_detail'))
        except PreRequisite.DoesNotExist:
            prereq = PreRequisite.objects.create(
                detail=request.POST.get('prereq_detail'))
        prereq.name = request.POST.get('prereq_name')
        prereq.year = request.POST.get('prereq_year')
        prereq.department = str(request.POST.get('prereq_dep'))
        if request.POST.get('prereq_ug') == 'on':
            prereq.ug = True
        if request.POST.get('prereq_pg') == 'on':
            prereq.pg = True
        prereq.save()
        print(prereq)
        print(form.errors)
        if form.is_valid():
            prereq.save()
            form.save()
            print("success")
            proj = Project.objects.get(
                project_name=request.POST.get('project_name'))
            proj.prerequisite = PreRequisite.objects.get(name=prereq.name)
            proj.save(update_fields=['prerequisite'])
            for p in request.POST.getlist('form.tags'):
                Project.objects.get(project_name=request.POST.get(
                    'project_name')).tags.add(str(p))
            professor = Professor.objects.get(project_name=proj.project_name)
            professor.imported = True
            professor.save(update_fields=['imported'])

            messages.success(request, 'Project was created successfully!')
            # Sending bulk emails on selecting checkbox turned off now
            '''
            if request.POST.get('update')=='on':
                project_name = request.POST.get('project_name')
                active_users = CustomUser.objects.filter(is_active=True)
                for each_user in active_users:
                    subject = 'FTP: New Project Added'
                    message = render_to_string('ftp/new_project_email.html', {
                        'user': each_user,
                        'project_name': project_name,
                    })
                    try:
                        alt_email = Profile.objects.filter(username=each_user).alt_email
                        email = EmailMessage(
                            subject, message, settings.EMAIL_HOST_USER, to=[
                                each_user.email, alt_email]
                        )
                    except:
                        email = EmailMessage(
                            subject, message, settings.EMAIL_HOST_USER, to=[each_user.email]
                        )
                    email.send(fail_silently=True)
                    '''
            return redirect('ftp:admin_projects')
        context = {"form": form, 'errors': form.errors}
        return render(request, 'ftp/admin/create_project.html', context)
    else:
        raise Http404('Page does not Exist')


def profile_create(request):
    user = request.user
    if user.is_irc:
        form = ProfileFormNew(request.POST or None)
        print(form.errors)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile was created successfully!')
            return redirect('ftp:admin_profiles')

        users = CustomUser.objects.all()
        context = {"form": form, 'errors': form.errors, "users": users}
        return render(request, 'ftp/admin/create_profile.html', context)
    else:
        raise Http404('Page does not Exist')


'''
def project_delete(request, pk):
    project = get_object_or_404(Project, id=pk)
    prereq = get_object_or_404(PreRequisite, name=project.prerequisite.name)
    prereq.delete()
    professor = get_object_or_404(Professor, name=project.professor_name)
    if project.deadline < datetime.date.today():
        # professor.delete()
         print("Past project deleted")
    else:
        professor.imported = False
        professor.save(update_fields=['imported'])
    project_name=project.project_name
    print(project.project_name)
    project.delete()
    messages.success(request, project_name + 'project was deleted successfully!')
    return redirect('ftp:admin_projects')
'''

'''
def profile_delete(request, pk):
    profile = get_object_or_404(Profile, id=pk)
    profile_name=profile.fullname
    profile.delete()

    messages.success(request, profile_name + 'profile was deleted successfully!')
    return redirect('ftp:admin_profiles')
'''


def project_display_change(request):
    data = {'fb': False}
    project_id = request.GET.get('pid', None)

    project = get_object_or_404(Project, id=project_id)
    print(project)
    if project.display:
        project.display = False
    else:
        project.display = True

    data = {'fb': True}

    project.save()

    return JsonResponse(data)


def admin_dyuti(request):
    user = request.user

    if user.is_irc:
        dyuti = Dyuti.objects.all()
        profile = get_object_or_404(Profile, username=request.user)
        # print(profiles)
        return render(request, 'ftp/admin/dyuti.html', {'alldyuti': dyuti, 'prof': profile})
    else:
        raise Http404('Page does not Exist')


def admin_hult(request):
    user = request.user

    if user.is_irc:
        hult = Hult.objects.all()
        # profile = get_object_or_404(Profile, username=request.user)
        # print(profiles)
        return render(request, 'ftp/admin/hult.html', {'allhult': hult})
    else:
        raise Http404('Page does not Exist')


def admin_hult_timer(request):
    user = request.user

    if user.is_irc:
        return render(request, 'ftp/admin/hult_timer.html', {'allhult': hult})
    else:
        raise Http404('Page does not Exist')


def hult(request):
    posters = HultPoster.objects.all()
    return render(request, 'ftp/hult.html', {'posters': posters})


@csrf_protect
def hult_register(request):
    if (request.method == "POST"):
        form = HultForm(request.POST or None, request.FILES or None)
        print("Uff")
        if form.is_valid():
            form.save()
            messages.success(request, 'Applied successfully!')
            return redirect('hult_register')
        else:
            print(form.errors)
            return render(request, 'ftp/hult_register.html', {'form': form, 'errors': form.errors})
    else:
        form = HultForm()
        return render(request, 'ftp/hult_register.html', {'form': form})


def hult_profile(request):
    user = request.user
    try:
        is_irc = user.is_irc
    except:
        return HttpResponse("<h1>You don't have permission to view this page</h1>")
    if user.is_irc:
        aid = request.GET.get('aid')
        team = Hult.objects.filter(id=aid)[0]
        # project = application.project
        # all_applied = project.profile.all()
        # profile = application.profile
        # applicants = Application.objects.filter(project=project)
        return render(request, 'ftp/admin/hult_team_profile.html', {'team': team})
    return HttpResponse("<h1>You don't have permission to view this page</h1>")


def admin_professors(request):
    user = request.user

    if user.is_irc:
        professors = []
        imported_profs = []
        allprofs = Professor.objects.all()
        # Searching for projects
        if request.GET.get('search'):
            search = request.GET.get('search')
            allprofs = Professor.objects.filter(Q(project_name__icontains=search) | Q(
                name__icontains=search) | Q(university_name__icontains=search))
        for professor in allprofs:
            if (professor.imported):
                imported_profs.append(professor)
            else:
                professors.append(professor)
        if request.GET.get('sort'):
            sort = request.GET.get('sort')
            if sort == 'created_at':
                professors.sort(key=lambda x: x.created_at, reverse=True)
                imported_profs.sort(key=lambda x: x.created_at, reverse=True)
            if sort == 'univ':
                professors.sort(key=lambda x: x.university_name.lower())
                imported_profs.sort(key=lambda x: x.university_name.lower())
            if sort == 'professor_name':
                professors.sort(key=lambda x: x.name.lower())
                imported_profs.sort(key=lambda x: x.name.lower())
            if sort == 'project_name':
                professors.sort(key=lambda x: x.project_name.lower())
                imported_profs.sort(key=lambda x: x.project_name.lower())
        profile = get_object_or_404(Profile, username=request.user)
        # print(profiles)
        return render(request, 'ftp/admin/professors.html', {'allprofessors': professors, 'importedprofs': imported_profs, 'prof': profile})
    else:
        raise Http404('Page does not Exist')


def admin_applications(request):
    user = request.user

    if user.is_irc:
        applications = Application.objects.all()
        # print(profiles)
        return render(request, 'ftp/admin/applications.html', {'allapplications': applications})
    else:
        raise Http404('Page does not Exist')


class ProjectUpdate(UpdateView):
    model = Project
    template_name = 'ftp/admin/edit_project.html'
    fields = ('professor_name', 'university', 'project_name', 'project_detail',
              'project_time', 'display', 'special', 'deadline', 'stipend', 'tags')
    success_url = reverse_lazy('ftp:admin_projects')

    def log_action(self):
        proj_name = self.get_object().project_name
        log = "[" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Edit_project | " + \
            self.request.user.username + " | " + proj_name + "</br>"
        logfile = open(os.path.join(settings.BASE_DIR,
                                    'templates/logs/dashboard_log.html'), "a")
        logfile.write(log)
        logfile.close()

    def form_valid(self, form):

        self.object = form.save()
        self.log_action()
        return super(ProjectUpdate, self).form_valid(form)


class ProfessorUpdate(UpdateView):
    model = Professor
    template_name = 'ftp/admin/edit_professor.html'
    fields = ('name', 'university_name', 'project_name', 'project_details',
              'prerequisites', 'no_of_students', 'duration', 'stipend', 'skype', 'imported')
    success_url = reverse_lazy('ftp:admin_professors')

    def log_action(self):
        professor_name = self.get_object().name
        log = "[" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Edit_professor | " + \
            self.request.user.username + " | " + professor_name + "</br>"
        logfile = open(os.path.join(settings.BASE_DIR,
                                    'templates/logs/dashboard_log.html'), "a")
        logfile.write(log)
        logfile.close()

    def form_valid(self, form):
        self.object = form.save()
        self.log_action()
        return super(ProfessorUpdate, self).form_valid(form)


def search_profile(request):
    if request.method == 'GET':
        search = request.GET.get('search')
        status = Profile.objects.filter(Q(fullname__icontains=search) | Q(rollno__icontains=search) | Q(
            department__icontains=search))  # filter returns a list so you might consider skip except part
        print(len(status))
        if not status:
            print("Empty")
            return render(request, 'ftp/admin/profiles.html',
                          context={'empty_search': 'No results found'})
        return render(request, 'ftp/admin/profiles.html', context={"allprofiles": status, "search_counts": len(status)})


def clear_search(request):
    return redirect('ftp:admin_profiles')


class ProfileUpdate(UpdateView):
    model = Profile
    template_name = 'ftp/admin/edit_profile.html'
    fields = ['fullname', 'department', 'contact', 'year', 'alt_email',
              'passport', 'transcript', 'cgpa', 'cv', 'photo', 'review', 'rollno']
    success_url = reverse_lazy('ftp:admin_profiles')

    def log_action(self):
        profile_name = self.get_object().fullname
        log = "[" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Edit_profile | " + \
            self.request.user.username + " | " + profile_name + "</br>"
        logfile = open(os.path.join(settings.BASE_DIR,
                                    'templates/logs/dashboard_log.html'), "a")
        logfile.write(log)
        logfile.close()

    def form_valid(self, form):
        self.object = form.save()
        self.log_action()
        return super(ProfileUpdate, self).form_valid(form)


def give_access(request):
    data = {'fb': False}
    user_id = request.GET.get('pid')
    user = get_object_or_404(CustomUser, id=user_id)
    print(user)

    if user.is_irc:
        user.is_irc = False
    else:
        user.is_irc = True

    data = {'fb': True}
    user.save()

    return JsonResponse(data)


def import_project(request):

    data = {'fb': False}
    professor_id = request.GET.get('pid')
    professor = get_object_or_404(Professor, id=professor_id)

    profile = get_object_or_404(Profile, username=request.user)
    projects = Project.objects.filter(project_name=professor.project_name)

    if len(projects) == 0:
        try:
            prereq = PreRequisite.objects.get(detail=professor.prerequisites)
        except PreRequisite.DoesNotExist:
            prereq = PreRequisite.objects.create(
                detail=professor.prerequisites)
        project = Project.objects.create(professor_name=professor.name, university=professor.university_name, project_name=professor.project_name,
                                         project_detail=professor.project_details, prerequisite=prereq, stipend=professor.stipend, project_time=professor.duration, currency=professor.currency)
        data = {'fb': True}

        returndict = {'data': data, 'project': project.id}
        # return render(request, 'ftp/admin/import_project.html')
        return JsonResponse(returndict)
    else:
        returndict = {'data': data, 'project': None}
        return JsonResponse(returndict)


def import_project_create(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    new_project = project
    print(project.currency)
    project.delete()

    print(new_project.id)

    return render(request, 'ftp/admin/import_project.html', {'project': new_project, 'tags': ProjectTag.objects.all()})


'''
def scholarship_delete(request, pk):
    scholarship = get_object_or_404(Scholarship, id=pk)

    scholarship.delete()

    return redirect("ftp:admin_scholarship")
'''


def admin_scholarships_create(request):
    form = NewScholarshipForm(request.POST or None)
    print(form.errors)
    if form.is_valid():
        form.save()
        messages.success(request, 'Scholarship was created successfully!')
        return redirect('ftp:admin_scholarship')

    users = CustomUser.objects.all()
    context = {"form": form, 'errors': form.errors, "users": users}
    return render(request, 'ftp/admin/create_scholarship.html', context)


class ScholarshipUpdate(UpdateView):
    model = Scholarship
    template_name = 'ftp/admin/edit_scholarship.html'
    fields = ['funding_agency', 'amount', 'scholarship_name',
              'scholarship_detail', 'display', 'deadline']
    success_url = reverse_lazy('ftp:admin_scholarship')

    def log_action(self):
        scholarship_name = self.get_object().scholarship_name
        log = "[" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Edit_scholarship | " + \
            self.request.user.username + " | " + scholarship_name + "</br>"
        logfile = open(os.path.join(settings.BASE_DIR,
                                    'templates/logs/dashboard_log.html'), "a")
        logfile.write(log)
        logfile.close()

    def form_valid(self, form):
        self.object = form.save()
        self.log_action()
        return super(ScholarshipUpdate, self).form_valid(form)


def addresult(request, pk):
    if request.method == 'POST':
        rolls = request.POST.getlist('result')
        profiles = Profile.objects.filter(rollno__in=rolls)
        proj = Project.objects.get(id=pk)
        try:
            Result.objects.get(project__id=proj.id)
            messages.success(request, 'Result already present.')
            return redirect('ftp:admin_projects')
        except Result.DoesNotExist:
            RESULT = Result.objects.create()
            # Project=project[::1]
            RESULT.project = proj
            for profile in profiles:
                for app in Application.objects.filter(project__id=proj.id):
                    if app.profile != profile:
                        app.status = str('Not Selected')
                    elif app.profile == profile:
                        app.status = str('Selected')
                    app.save()
                profile.selected = True
                RESULT.result.add(profile)
                profile.save()
                RESULT.save()

            messages.success(request, 'Result added successfully!')

            log = "[" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Added_result | " + \
                request.user.username + " | " + proj.project_name + "</br>"
            logfile = open(os.path.join(settings.BASE_DIR,
                                        'templates/logs/dashboard_log.html'), "a")
            logfile.write(log)
            logfile.close()

            return redirect('ftp:admin_projects')

    else:
        return redirect('ftp:admin_projects')


def change_display_scho(request):
    data = {'fb': False}
    pid = request.GET.get('pid')

    scholarship = get_object_or_404(Scholarship, id=pid)

    if scholarship.display:
        scholarship.display = False
    else:
        scholarship.display = True

    scholarship.save()
    data = {'fb': True}

    return JsonResponse(data)


def change_prof_display(request):
    data = {'fb': False}
    app_id = request.GET.get('app_id')
    print(app_id)

    application = get_object_or_404(Application, id=app_id)

    if application.display_prof:
        application.display_prof = False
    else:
        application.display_prof = True

    application.save()
    data = {'fb': True}

    return JsonResponse(data)


def edit_prereq(request, name):
    project = get_object_or_404(Project, project_name=name)
    prereq = project.prerequisite

    if request.method == 'POST':
        if prereq is None:
            prereq = PreRequisite.objects.create()
            project.prerequisite = prereq
            project.save(update_fields=['prerequisite'])
        prereq.pg = True if request.POST.get('pg') else False
        prereq.ug = True if request.POST.get('pg') else False
        print(prereq.ug, prereq.pg)
        if request.POST.get('name') != '':
            prereq.name = request.POST.get('name')

        if request.POST.get('year') != '':
            prereq.year = request.POST.get('year')

        if request.POST.get('department') != '':
            prereq.department = request.POST.get('department')

        prereq.save()

        log = "[" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] Edit_prerequisite | " + \
            request.user.username + " | " + prereq.name[:10] + "....</br>"
        logfile = open(os.path.join(settings.BASE_DIR,
                                    'templates/logs/dashboard_log.html'), "a")
        logfile.write(log)
        logfile.close()

        return redirect(reverse_lazy('ftp:admin_projects'))
    else:
        return render(request, 'ftp/admin/edit_prereq.html', {'prereq': prereq})


def admin_logs(requenst):
    return render(requenst, 'logs/dashboard_log.html')


def feedback_form(request):
    if request.method == 'POST':
        print('Oivkvbkvfvjkerbjk---------------------')
        form = FeedBackForm(request.POST or None)
        print(form.errors)

        if form.is_valid():
            feedBACK = FeedBack_PROF()
            feedBACK.professor_name = form['professor_name'].value()
            feedBACK.university_name = form['university_name'].value()
            feedBACK.student_name = form['student_name'].value()
            feedBACK.passionate_marks = form['passionate_marks'].value()
            feedBACK.satisfaction_marks = form['satisfaction_marks'].value()
            feedBACK.ethics_marks = form['ethics_marks'].value()
            feedBACK.creative_marks = form['creative_marks'].value()
            feedBACK.overall_marks = form['overall_marks'].value()
            feedBACK.suggestions = form['suggestions'].value()
            feedBACK.feedback = form['feedback'].value()

            feedBACK.save()

            messages.success(
                request, 'FeedBack submitted successfully successfully!')

            return render(request, 'ftp/feedback/feedback_success.html')

        else:
            print(form)
            context = {"form": form, 'errors': form.errors}
            return render(request, 'ftp/feedback/create_feedback.html', context)
    else:
        form = FeedBackForm()
        context = {"form": form}
        return render(request, 'ftp/feedback/create_feedback.html', context)


def feedback_form_stu(request):
    if request.method == 'POST':
        print('Oivkvbkvfvjkerbjk---------------------')
        form = FeedBackFormStu(request.POST or None)
        print(form.errors)

        if form.is_valid():

            feedBACK = FeedBack_stu()
            feedBACK.professor_name = form['professor_name'].value()
            feedBACK.university_name = form['university_name'].value()

            feedBACK.Professor_email = form['Professor_email'].value()
            feedBACK.student_name = form['student_name'].value()

            feedBACK.relevant_work = form['relevant_work'].value()
            feedBACK.supportive = form['supportive'].value()
            feedBACK.satisfied = form['satisfied'].value()
            feedBACK.rate_marks = form['rate_marks'].value()
            feedBACK.interview = form['interview'].value()
            feedBACK.feedback = form['feedback'].value()
            feedBACK.suggestions = form['suggestions'].value()

            feedBACK.save()

            messages.success(
                request, 'FeedBack submitted successfully successfully!')

            return render(request, 'ftp/feedback/feedback_success.html')

        else:
            print(form)
            context = {"form": form, 'errors': form.errors}
            return render(request, 'ftp/feedback/student_feedback.html', context)
    else:
        form = FeedBackForm()
        context = {"form": form}
        return render(request, 'ftp/feedback/student_feedback.html', context)


def Add_tags(request):
    user = request.user
    if user.is_irc:
        proj_tag = ProjectTag.objects.all()
        if request.method == 'POST':
            title = request.POST.get('title')
            if not ProjectTag.objects.filter(title=title).exists():
                ProjectTag.objects.create(
                    title=title,
                )
            return render(request, "ftp/admin/Add_Project_tag.html", {'p_tag': proj_tag})
        else:
            return render(request, "ftp/admin/Add_Project_tag.html", {'p_tag': proj_tag})
    else:
        raise Http404('Page does not Exist')


def showstatus(request, project_id):
    user = request.user
    if user.is_irc:
        project_status = Application.objects.filter(project=project_id)
        print("DSfdsfsdfdsf")
        print(project_status)
        project_name = project_status[0].project
        allprofile = Profile.objects.all()
        if request.method == "POST":
            name = request.POST.get('name')
            projectname = project_name
            ustatus = str(request.POST.get('userstatus'))
            uid = request.POST.get('id')
            n = name
            Application.objects.filter(id=uid).update(status=str(ustatus))
            if ustatus == "Selected":
                print("success")
                print(Result.objects.get(project=project_name))
                if Result.objects.get(project=project_name) is not None:
                    k = Profile.objects.get(id=name)
                    k.selected = True
                    k.save()
                    a = Result.objects.get(project=project_name)
                    print(a)
                    p = []
                    y = a.project
                    for x in a.result.all():
                        p.append(x)
                    p.append(k)
                    print(p)
                    Result.objects.get(project=project_name).delete()
                    RESULT = Result.objects.create()
                    RESULT.project = y
                    for profile in p:
                        RESULT.result.add(profile)
                        RESULT.save()
            if ustatus == "Not Selected":
                if Result.objects.get(project=project_name) is not None:
                    k = Profile.objects.get(id=name)
                    k.selected = False
                    k.save()
                    a = Result.objects.get(project=project_name)
                    p = []
                    y = a.project
                    for x in a.result.all():
                        p.append(x)
                    p.remove(k)
                    print(p)
                    Result.objects.get(project=project_name).delete()
                    RESULT = Result.objects.create()
                    RESULT.project = y
                    for profile in p:
                        RESULT.result.add(profile)
                        RESULT.save()

            msg = Profile.objects.get(
                id=name).rollno+" Updation Successfull to " + ustatus.upper()

            return render(request, 'ftp/Status_Edit.html', {'projectstatus': project_status, 'user': allprofile, 'pname': project_name, 'msg': msg})

        else:
            return render(request, 'ftp/Status_Edit.html', {'projectstatus': project_status, 'user': allprofile, 'pname': project_name})
    else:
        raise Http404('Page does not Exist')


def status_default(request, project_id):
    user = request.user
    if user.is_irc:
        for app in Application.objects.filter(project=Project.objects.get(id=project_id)):
            app.status = "Pending"
            app.save()
            print(app.status)

        return redirect(reverse_lazy('ftp:admin_projects'))
    else:
        raise Http404('Page does not Exist')


def project_csv(request):
    user = request.user
    if user.is_irc:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename = Project.csv'
        writer = csv.writer(response)
        project = Project.objects.all()

        writer.writerow(['professor_name', 'university', 'project_name', 'project_detail',
                         'project_mode', 'project_time', 'deadline', 'prerequisite', 'stipend', 'tags'])

        for p in project:
            lis = []
            for k in p.tags.all():
                lis.append(k.title)

            writer.writerow([p.professor_name, p.university, p.project_name, p.project_detail,
                             p.project_mode, p.project_time, p.deadline, p.prerequisite, p.stipend, lis])
            print(p.deadline.strftime("%d/%m/%Y"))

        return response
    else:
        return Httpresponse("<h1>PAge Not Found</h1>")


def professor_csv(request):
    user = request.user
    if user.is_irc:

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename = Professor.csv'
        writer = csv.writer(response)
        professor = Professor.objects.all()

        writer.writerow(['professor_name', 'university_name', 'project_name',
                         'no_of_students', 'prerequisites', 'duration', 'stipend', 'skype', 'created_at'])

        for p in professor:
            writer.writerow([p.name, p.university_name, p.project_name, p.no_of_students,
                             p.prerequisites, p.duration, p.stipend, p.skype, p.created_at])

        return response
    else:
        return Httpresponse("<h1>PAge Not Found</h1>")


def resultss(request, project_id):
    user = request.user
    if user.is_irc:
        project_status = Application.objects.filter(project=project_id)
        print('kk')
        print("DSfdsfsdfdsf")
        print(project_status)
        project_name = project_status[0].project
        allprofile = Profile.objects.all()
        if request.method == "POST":
            name = request.POST.get('name')
            projectname = project_name
            ustatus = str(request.POST.get('userstatus'))
            uid = request.POST.get('id')
            n = name
            Application.objects.filter(id=uid).update(status=str(ustatus))
            try:
                if ustatus == "Selected":
                    print("success")
                    # print(Result.objects.get(project=project_name))
                    if Result.objects.get(project=project_name) is not None:
                        k = Profile.objects.get(id=name)
                        k.selected = True
                        k.save()
                        a = Result.objects.get(project=project_name)
                        print(a)
                        p = []
                        y = a.project
                        for x in a.result.all():
                            p.append(x)
                        p.append(k)
                        print(p)
                        Result.objects.get(project=project_name).delete()
                        RESULT = Result.objects.create()
                        RESULT.project = y
                        RESULT.save()
                        for profile in p:
                            RESULT.result.add(profile)
                            RESULT.save()
                if ustatus == "Not Selected":
                    if Result.objects.get(project=project_name) is not None:
                        k = Profile.objects.get(id=name)
                        k.selected = False
                        k.save()
                        a = Result.objects.get(project=project_name)
                        p = []
                        y = a.project
                        for x in a.result.all():
                            p.append(x)
                        p.remove(k)
                        print(p)
                        Result.objects.get(project=project_name).delete()
                        RESULT = Result.objects.create()
                        RESULT.project = y
                        RESULT.save()
                        for profile in p:
                            RESULT.result.add(profile)
                            RESULT.save()
            except:
                return HttpResponse("<h1>Add this project to the result to update</h1>")

            msg = Profile.objects.get(
                id=name).rollno+" Updation Successfull to " + ustatus.upper()

            return render(request, 'ftp/resultss.html', {'projectstatus': project_status, 'user': allprofile, 'pname': project_name, 'msg': msg})

        else:
            return render(request, 'ftp/resultss.html', {'projectstatus': project_status, 'user': allprofile, 'pname': project_name})
    else:
        raise Http404('Page does not Exist')


def scholarship_csv(request):
    user_ = request.user
    if user_.is_irc:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename = Scholarship.csv'
        writer = csv.writer(response)
        application = Scholarship_appli.objects.all()

        writer.writerow(['name', 'Scholarship_name', 'Roll_Number', 'Department', 'Email', 'FacAd', 'HOD', 'Host_Institution', 'Year_of_Graduation', 'DOV(from)', 'DOV(to)', 'proposed research/professional internship', 'SOP', 'History of Collaboration (if any) with the host institution/company',
                         'Justification of applying through (IITKGP) USA Award Program', 'Possible outcome of your proposed research/ professional internship', 'How your engagement with the Host Institute/company will be beneficial to IIT KGP', 'CV', 'Awards', 'Transcript', 'NOC', 'LOE', 'Work Publication', 'fuding proof', 'offer Letter', 'Reviewed by'])

        for p in application:
            if p.Awards:
                awards = 'https://ircell.iitkgp.ac.in' + str(p.Awards.url)
            else:
                awards = None

            if p.letter_of_endorsement:
                loe = 'http://ircell.iitkgp.ac.in' + \
                    str(p.letter_of_endorsement.url)
            else:
                loe = None

            if p.work_publication:
                wp = 'http://ircell.iitkgp.ac.in' + str(p.work_publication.url)
            else:
                wp = None

            if p.fuding_proof:
                fp = 'http://ircell.iitkgp.ac.in' + str(p.fuding_proof.url)
            else:
                fp = None
            writer.writerow([p.name, p.scholarship.scholarship_name, p.roll, p.department, p.email, p.NameofFacultyAdvisor, p.NameofHOD, p.Nameofhostinstitution, p.yearOfGrad, p.DurationOfVisit_from, p.DurationOfVisit_to, p.DetailsOfTheProposedResearch_or_professionalInternship, p.sop, p.HistoryOfCollobration, p.Justification_of_applying_through_the_IITKGF_Of_USA_AwardProgram,
                             p.DetailsOfTheProposedResearch_or_professionalInternship, p.Explain_in_about_250_words_how_your_engagement_with_the_Host_Institute, 'https://ircell.iitkgp.ac.in' + p.cv.url, awards, 'https://ircell.iitkgp.ac.in' + p.Transcript.url, 'https://ircell.iitkgp.ac.in' + p.NOC.url, loe, wp, fp, 'https://ircell.iitkgp.ac.in' + p.offer_letter.url, p.reviewed_by])

        return response
    else:
        return HttpResponse("<h1>PAge Not Found</h1>")


def hult_info(request):
    hult_all = HultInfo.objects.all()
    ideas = []
    prob_solns = []
    teams = []
    pitchs = []
    impacts = []
    for single in hult_all:
        if single.title == "Idea":
            ideas.append(single)
        elif single.title == "Problem + Solution":
            prob_solns.append(single)
        elif single.title == "Team":
            teams.append(single)
        elif single.title == "Pitch":
            pitchs.append(single)
        elif single.title == "Impact":
            impacts.append(single)
    return render(request, 'hult_info.html', {'ideas': ideas, 'prob_solns': prob_solns, 'teams': teams, 'pitchs': pitchs, 'impacts': impacts})


def show_info(request, id):
    info = HultInfo.objects.filter(id=id)
    if info[0].links:
        links = InfoLink.objects.filter(title=info[0].subtitle)
        return render(request, 'inner_info.html', {'info': info, 'links': links})
    return render(request, 'inner_info.html', {'info': info})


def blogs(request):
    return render(request, 'home/blogs.html')
# def requestTopic(request):
# 	if request.user.is_authenticated:
# 		try:
# 			profile = Profile.objects.get(username=request.user)
# 			# profile = Profile.objects.get(id=id)
# 			form = ProfileForm(instance=profile)  # prepopulate the form with an existing band
# 			return render(request,'listings/band_update.html',{'form': form})
# 		except Profile.DoesNotExist:
# 			return redirect('ftp:create_profile')
# 	else:
# 		return redirect('ftp:login_user')
