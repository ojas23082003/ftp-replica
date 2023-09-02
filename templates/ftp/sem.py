import csv
import datetime
import os

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import resolve, reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import *
from .models import *
from .tokens import account_activation_token, forgot_password_token

# import tablib


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            print('form valid')
            user = form.save(commit=False)
            print(user)
            email = str(form.cleaned_data.get('username')).lower()
            if "@iitkgp.ac.in" not in email:
                email = email + '@iitkgp.ac.in'
            if "@iitkgp.ac.in" in email:
                username = email.split('@')[0]
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            user.username = username.lower()
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
            email = EmailMessage(
                subject, message, to=[user.email]
            )
            email.send()
            print(message)
            print(email)
            return render(request, 'ftp/login/Email_sent.html', context={'email': user.email})
        else:
            print(form.errors)
            return render(request, 'ftp/login/register.html', {'form': form, 'errors': form.errors})

    else:
        form = CustomUserCreationForm()
        return render(request, 'ftp/login/register.html', {'form': form})


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
	    current_site = get_current_site(request)
	    subject = 'FTP: Account Activation'
        message = render_to_string('ftp/account_activation_email.html', {
           'user': user,
           'domain': current_site.domain,
           'uid': urlsafe_base64_encode(force_bytes(user.pk)),
           'token': account_activation_token.make_token(user),
        })
        email = EmailMessage(
        subject, message, to=[user.email]
        )
        email.send()
        print(message)
        return render(request, 'ftp/login/Email_sent.html', context={'email': user.email})


    else:
        user.is_active = True
        user.save()
        return redirect('ftp:login_user')



def new_profile(request):
    if not request.user.is_authenticated:
        return render(request, 'login.html')
    else:
        if len(Profile.objects.filter(username=request.user.id)) == 0:
            roll = request.user.username
            dep = roll[2:4]

            pr_year = 20 - int(roll[0:2])
            # is_allowed = (int(roll[4]) >= 6)
            # if pr_year > 1 or is_allowed:
            #     logout(request)
            #     form = CustomUserCreationForm()
            #     return render('ftp/login/register.html', {'form': form}, context={'errors': 'Not allowed to register'})

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
            elif (pr_year):
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
        username = request.POST['email']
        if '@iitkgp.ac.in' in username:
            username = username.split("@")[0]
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                try:
                    profile = Profile.objects.get(username=request.user)
                    print(profile.photo)
                    if profile.photo == "":
                        messages.success(request, "Please add your photo")
                        return redirect('ftp:edit_profile')
                    if profile.updated == False:
                        profile.updated=True
                        profile.save()
                        return render(request,'ftp/profile/edit_profile.html',{'updated':True})

                    return redirect('ftp:projects')
                except Profile.DoesNotExist:
                    return redirect('ftp:create_profile')
            else:
                return render(request, 'ftp/login/login.html', {'error': 'Your account is not active'})
        else:
            return render(request, 'ftp/login/login.html', {'error': 'Invalid login'})
    else:
        return render(request, 'ftp/login/login.html')


def logout_user(request):
    logout(request)
    return redirect('ftp:login_user')


def create_profile(request):
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
        print(request.POST.get("department"))
        # roll = request.user.username
        # dep = roll[2:4]
        # pr_year = 20-int(roll[0:2])

        # if(pr_year==1):
        #      print(str(pr_year)+'st')
        # elif(pr_year==2):
        #      print(str(pr_year)+'nd')
        # elif(pr_year):
        #      print(str(pr_year)+'rd')
        # else:
        #      print(str(pr_year)+'th')

        if form.is_valid():
            print(form.errors)
            # form.save(commit=False).username = request.user.id
            make_prof = form.save(commit=False)
            print(request.user)
            make_prof.username = request.user
            roll = make_prof.rollno
            pr_year = 20 - int(roll[0:2])
            is_allowed = (int(roll[4]) >= 4)
            if pr_year <= 1 and not is_allowed:
                logout(request)
                error = 'First years are ineligible to register. Try again next year.'
                request.user.is_active = False
                print(error)
                return render(request, 'ftp/login/login.html', {'error': error})
            make_prof.save()

            prof = Profile.objects.filter(fullname=request.POST['fullname'])
            print(prof)
            prof.update(review='NO')
            print(form.errors)
            return redirect('ftp:projects')
        else:
            print(form.errors)
            return render(request, 'ftp/profile/index.html',
                          {'roll': request.user, 'form': form, 'errors': form.errors})


def view_projects(request):
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        try:
            profile = Profile.objects.get(username=request.user)
        except Profile.DoesNotExist:
            return redirect('ftp:create_profile')

        rem_project = Project.objects.exclude(id__in=[x.id for x in profile.project.all()])
        # rem_project = Project.objects.exclude(id__in=[x.project.id for x in Application.objects.filter(profile=profile)])
        current_time = datetime.datetime.now().date()
        bookmarked = Project.objects.filter(bookmarks=profile)
        for proj in rem_project:
            if current_time > proj.deadline:
                proj.display = False
                # print('qwerty')

        success = True

        for proj in rem_project:
            if proj.display:
                success = False

            if proj.prerequisites:
                prerequisite = proj.prerequisites

                dep = profile.rollno[2:4].lower()
                year = 20 - int(profile.rollno[0:2])
                pg = (int(profile.rollno[4]) > 5)
                ug = not pg

                if prerequisite.department is not None:
                    predeps = prerequisite.department.strip().split(',')
                else:
                    predeps = ['']
                predeps = [p.lower() for p in predeps]
                if prerequisite.year != None:
                    preyear = prerequisite.year.strip().split(',')
                else:
                    preyear = ['']

                successdep = True
                successyear = True
                successugpg = False

                if prerequisite.ug == False and prerequisite.pg == False:
                    successugpg = True
                else:
                    if prerequisite.ug == ug:
                        successugpg = True
                    if prerequisite.pg == pg:
                        successugpg = True

                if predeps[0] == '':
                    successdep = True
                elif dep not in predeps:
                    successdep = False

                if preyear[0] == '':
                    successyear = True
                elif year not in preyear:
                    successyear = False

                if successdep and successyear and successugpg:
                    proj.reason = None
                    proj.save()
                else:
                    proj.reason = 'You are not eligible to apply for this project'
                    proj.save()

        pastproject = Project.objects.all()

        return render(request, 'ftp/ProjectsPage/projects.html',
                      {"success": success, 'allprojects': rem_project, 'prof': profile, 'bookmarks': bookmarked,
                       'pastproject': pastproject,
                       'date': current_time})


def view_scholarships(request):
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        try:
            profile = Profile.objects.get(username=request.user)
        except Profile.DoesNotExist:
            return redirect('ftp:create_profile')

        rem_scholarship = Scholarship.objects.exclude(id__in=[x.id for x in profile.scholarship.all()])

        current_time = datetime.datetime.now().date()
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
                      {"success": success, 'allprojects': rem_scholarship, 'prof': profile, 'bookmarks': bookmarked})


def yourscholarships(request):
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        try:
            profile = Profile.objects.get(username=request.user)
        except Profile.DoesNotExist:
            return redirect('ftp:create_profile')

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
                      {"success": success, 'allprojects': rem_scholarship, 'prof': profile})


def apply(request, scholarship_id):
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:

        return render(request, 'ftp/Scholarship/apply.html')


def view_results(request):
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        try:
            profile = Profile.objects.get(username=request.user)
        except Profile.DoesNotExist:
            return redirect('ftp:create_profile')
        res = Result.objects.all()
        return render(request, 'ftp/results/index.html', {'prof': profile, 'result': res})


def already_applied(request):
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        try:
            profile = Profile.objects.get(username=request.user)
        except Profile.DoesNotExist:
            return redirect('ftp:create_profile')

        # applied_projects = profile.project.all()
        success = True
        applied_projects_app = Application.objects.filter(profile=profile)
        # applied_projects_app = [[x.project, x.sop, x.ncv] for x in applied_projects_app]
        applied_projects = []
        # application = []

        bookmarked = Project.objects.filter(bookmarks=profile)

        for app in applied_projects_app:
            success = False
            applied_projects.append([app.project, app.sop, app.ncv])

        # for app in applied_projects_app:
        #     application.append(app.sop)

        return render(request, 'ftp/ProjectsPage/yourapplications.html',
                      {'allprojects': applied_projects, 'prof': profile, "success": success, "bookmarks": bookmarked})


def applied_students(request, project_id):
    proj = get_object_or_404(Project, id=project_id)
    all_applied = proj.profile.all()
    success = False
    if len(all_applied) != 0:
        success = True

    return render(request, 'ftp/profview/base.html', {'all_applied': all_applied, 'success': success, 'project': proj})


def view_frame(request, profile_id, project_id):
    all_applied = get_object_or_404(Profile, id=profile_id)
    proj_applied = get_object_or_404(Project, id=project_id)
    pro = get_object_or_404(Application, profile=all_applied, project=proj_applied)
    return render(request, 'ftp/profview/frame.html', {'all_applied': all_applied, 'pro': pro, 'project': proj_applied})


def apply_project(request, project_id):
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        try:
            project = Project.objects.get(id=project_id)
            profile = Profile.objects.get(username=request.user)
            ncv = request.FILES.get('ncv', None)
            sop = request.POST.get('sop', None)
            Loi = request.POST.get('Loi', None)
            if project.display:
                Application.objects.create(profile=profile, project=project, sop=sop, ncv=ncv, Loi=Loi)

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


def apply_scholarship(request):
    if not request.user.is_authenticated:
        return render(request, 'ftp/login/login.html')
    else:
        form = ScholarshipForm(request.POST or None, request.FILES or None)
        scholarship_id = request.path_info[24:-1]

        print(form.errors)
        if form.is_valid():
            scholarship = get_object_or_404(Scholarship, id=scholarship_id)
            temp = form.save(commit=False)
            profile = get_object_or_404(Profile, username=request.user)
            temp.scholarship = scholarship
            temp.profile = profile
            temp.Transcripts = profile.transcript
            scholarship.display = False
            scholarship.save()
            form.save()
            messages.success(request, 'Applied successfully!')
            return redirect('ftp:scholarships')
        context = {"form": form, 'errors': form.errors}
        return render(request, 'ftp/Scholarship/apply.html', context)


# def apply_scholarships(request, scholarship_id):
#     if not request.user.is_authenticated():
#         return render(request, 'login.html')
#     else:
#         print(scholarship_id)
#         project = Scholarship.objects.filter(pk=scholarship_id)[0]
#         if project.display:
#             print(Scholarship.objects.filter(pk=scholarship_id)[0].funding_agency)
#             return render(request, 'scholarshipdetail.html', {'project': project})
#         else:
#             logout(request)
#             form = UserCreationForm(request.POST or None)
#             context = {
#                 "form": form,
#                 "message": "You have been forcefully logged out.",
#             }
#             return render(request, 'login.html', context)
#
#
# def apply_finish_scholarships(request,  scholarship_id):
#     if not request.user.is_authenticated():
#         return render(request, 'login.html')
#     else:
#         print(scholarship_id)
#         if request.method == "POST":
#             form = ApplyScholarshipForm(request.POST, request.FILES)
#             print(form.errors)
#             napp = form.save(commit=False)
#             napp.user = request.user
#             napp.scholarship = Scholarship.objects.filter(pk=scholarship_id)[0]
#             # napp.profname = Projects.objects.filter(pk=project_id)[0].professor_name
#             napp.profile = Profile.objects.filter(username=request.user.id)[0]
#             # napp.funding_agency = Scholarship.objects.filter(pk=project_id)[0].funding_agency
#             napp.save()
#             # print(napp.profname)
#
#             # application = Applied.objects.filter(sop=request.POST['sop'])
#             # print(1)
#             # application.update(user=request.user.id)
#             # print(2)
#             # application.update(project=project_id)
#             # print(3)
#             # application.update(profile=Profile.objects.filter(username=request.user.id)[0].id)
#             # print(4)
#             # form.save()
#             return redirect('/ftp/portal/scholarships/')


def forgotpass(request):
    User = get_user_model()
    print("Not Post")
    if request.method == 'POST':
        username = request.POST.get('username')
        user = User.objects.get(username=username)
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
            mail_subject, message, to=[user.email]
        )
        print(message)
        email.send()
        print("email send")
        return render(request, 'ftp/login/Email_sent.html', context={'email': user.email})
    else:
        return render(request, 'ftp/login/forgot_password_form.html')


def pass_reset(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and forgot_password_token.check_token(user, token):
        username = user.username
        return render(request, 'ftp/login/password_reset_form.html', {'username': username})
    else:
        return HttpResponse('Password reset link is invalid!')


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
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    else:
        profile = Profile.objects.get(username=request.user.id)
        print(profile.fullname)
        if len(Profile.objects.filter(username=request.user.id)) == 1:
            return render(request, 'editprofile.html', {'profile': profile})
        else:
            return redirect('/ftp/portal/projects/')


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
            skype = request.POST.get('skype', None)

            print(contact, passport, cgpa, skype)

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

            if skype:
                profile.skype = skype

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
#     if not request.user.is_authenticated():
#         return render(request, 'login.html')
#     else:
#         allresults = Results.objects.all()
#         return render(request, 'results.html', {'allresults': allresults})
#
#
# def scholarshipresults(request):
#     if not request.user.is_authenticated():
#         return render(request, 'login.html')
#     else:
#         allresults = ScholarshipResults.objects.all()
#         return render(request, 'scholarshipresults.html', {'allresults': allresults})
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
            bookmarked = Project.objects.filter(bookmarks=profile)
            success = True

            for e in bookmarked:
                success = False
                break

            applied_projects_app = Application.objects.filter(profile=profile)
            applied_projects = []
            for app in applied_projects_app:
                applied_projects.append(app.project)

            return render(request, 'ftp/ProjectsPage/bookmarks.html',
                          {"success": success, 'allprojects': bookmarked, 'prof': profile, 'applieds': applied_projects,
                           'app': applied_projects_app})


def add_favorite(request):
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')
    else:
        data = {'fb': False}
        project_id = request.GET.get('pid', None)
        try:
            project = Project.objects.get(id=project_id)
            profile = Profile.objects.get(username=request.user)

            all_bookmarks = Project.objects.filter(bookmarks=profile)
            if project not in all_bookmarks:
                project.bookmarks.add(profile)
            else:
                project.bookmarks.remove(profile)

            data = {'fb': True}
            return JsonResponse(data)
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
        return render(request, 'ftp/profile/view_profile.html', {"profile": profile})


def edit_profile(request):
    print("User enter edit function")
    if not request.user.is_authenticated:
        return redirect('ftp:login_user')

    try:
        profile = Profile.objects.get(username=request.user)
    except Profile.DoesNotExist:
        return redirect('ftp:create_profile')

    if request.method == 'POST':
        print("POSTED USER")
        fs = FileSystemStorage()
        print(profile.fullname)
        photo = request.FILES.get('photo', None)
        # passport = request.POST.get('passport', None)
        cgpa = request.POST.get('cgpa', None)
        cv = request.FILES.get('cv', None)
        transcript = request.FILES.get('transcript', None)
        contact = request.POST.get('contact', None)
        skype = request.POST.get('skype', None)
        print(contact, cgpa, skype)

        if photo:
            ext = os.path.splitext(photo.name)[1]
            pathname = request.user.username + "_p" + upload_time() + ext
            fs.save(pathname, photo)
            # if profile.photo.name:
            #     fs.delete(profile.photo.name)
            profile.photo.name = pathname

        # if passport:
        #     profile.passport = passport

        if cgpa:
            profile.cgpa = cgpa

        if cv:
            ext = os.path.splitext(cv.name)[1]
            pathname = request.user.username + "_c" + upload_time() + ext
            fs.save(pathname, cv)
            # fs.delete(profile.cv.name)
            profile.cv.name = pathname

        if contact:
            profile.contact = contact

        if skype:
            profile.skype = skype

        if transcript:
        # if request.user.username not in profile.transcript.name:
            ext = os.path.splitext(transcript.name)[1]
            pathname = request.user.username + "_t" + upload_date() + ext
            fs.save(pathname, transcript)
            # fs.delete(profile.transcript.name)
            profile.transcript.name = pathname
            # else:
            #     profile.save()
            #     print("Transcript problem")
            #     return render(request, 'ftp/profile/edit_profile.html', {'profile': profile,
            #                                                              'errors': "Transcript update failed. Transcript can be updated only after five days of its last update."})

        profile.save()
        print("Profile save edited")
        return redirect('ftp:projects')
    else:
        return render(request, 'ftp/profile/edit_profile.html', {'profile': profile})


# def dyuti(request):
#     form = DyutiForm(request.POST or None)
#     if form.is_valid():
#         tp = form.save(commit=False)
#         cours = request.POST.getlist('course')
#

def admin_projects(request):
    user = request.user

    if user.is_irc:
        projects = Project.objects.all()
        profilee = Profile.objects.all()
        profile = get_object_or_404(Profile, username=request.user)
        display = []
        professors = Professor.objects.all()
        for project in projects:
            applications = Application.objects.filter(project=project)
            display.append([project, applications])

        print(display)
        return render(request, 'ftp/admin/projects.html',
                      {'displaylist': display, 'allprofessors': professors, 'prof': profile, 'profilee': profilee})
    else:
        raise Http404('Page does not Exist')


def admin_scholarship(request):
    user = request.user

    if user.is_irc:
        scholarship = Scholarship.objects.all()

        info = []
        for scho in scholarship:
            application = Scholarship_appli.objects.filter(scholarship=scho)

            info.append([scho, application])

        profile = get_object_or_404(Profile, username=request.user)
        return render(request, 'ftp/admin/scholarship.html', {'scholarship': info})
    else:
        raise Http404('Page does not Exist')


def admin_profiles(request):
    user = request.user

    if user.is_irc:
        profiles = Profile.objects.all()
        profile = get_object_or_404(Profile, username=request.user)
        # print(profiles)
        return render(request, 'ftp/admin/profiles.html', {'allprofiles': profiles, 'prof': profile})
    else:
        raise Http404('Page does not Exist')


def export_profile(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Profile List.csv"'
    writer = csv.writer(response)
    writer.writerow(['username', 'fullname', 'department', 'contact', 'year', 'skype', 'passport', 'cgpa', 'rollno'])
    profile = Profile.objects.all().values_list('username', 'fullname', 'department', 'contact', 'year', 'skype',
                                                'passport', 'cgpa', 'rollno')
    for each_profile in profile:
        writer.writerow(each_profile)
    return response


def export_hult(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Hult List.csv"'
    writer = csv.writer(response)
    writer.writerow(
        ['team_name', 'email_leader', 'member_2', 'email_mem2', 'member_3', 'email_mem3', 'member_4', 'email_mem4',
         'queries'])
    hult = Hult.objects.all().values_list('team_name', 'email_leader', 'member_2', 'email_mem2', 'member_3',
                                          'email_mem3', 'member_4', 'email_mem4', 'queries')
    for each_hult in hult:
        writer.writerow(each_hult)
    return response


def export_dyuti(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Dyuti List.csv"'
    writer = csv.writer(response)
    writer.writerow(
        ['first_name', 'last_name', 'phone', 'email', 'gender', 'country', 'passport_no', 'visa_no', 'visa_cate',
         'visa_validity', 'uni_india', 'state', 'city', 'department', 'year_of_study', 'reg_no', 'is_scholarship'])
    dyuti = Dyuti.objects.all().values_list('first_name', 'last_name', 'phone', 'email', 'gender', 'country',
                                            'passport_no', 'visa_no', 'visa_cate', 'visa_validity', 'uni_india',
                                            'state', 'city', 'department', 'year_of_study', 'reg_no', 'is_scholarship')
    for each_dyuti in dyuti:
        writer.writerow(each_dyuti)
    return response


def export_applied_list(request, pk):
    project = Project.objects.get(pk=pk)
    query_set = project.application_set.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=" ' + project.project_name + ' List.csv"'
    writer = csv.writer(response)
    writer.writerow(
        ['Username', 'Fullname', 'Roll No', 'Contact No', 'Department', 'CV', 'SOP', 'Letter of Importance'])

    for each in query_set:

        # writer.writerow([each.profile.username, each.profile.fullname,each.profile.rollno, each.profile.contact, each.profile.department])

        if each.ncv:
            writer.writerow([each.profile.username, each.profile.fullname, each.profile.rollno, each.profile.contact,
                             each.profile.department, 'https://ircell.iitkgp.ac.in' + each.ncv.url, each.sop, each.Loi])
        else:
            writer.writerow([each.profile.username, each.profile.fullname, each.profile.rollno, each.profile.contact,
                             each.profile.department, 'https://ircell.iitkgp.ac.in' + each.profile.cv.url, each.sop,
                             each.Loi])


def project_create(request):
    form = ProjectForm(request.POST or None)
    print(form.errors)
    if form.is_valid():
        prerequisite = PreRequisite()
        prerequisite.name = form['project_name'].value()
        prerequisite.ug = request.POST.get('ug') != None
        prerequisite.pg = request.POST.get('pg') != None
        prerequisite.year = request.POST.get('year')
        prerequisite.department = request.POST.get('department')
        prerequisite.save()
        form_temp = form.save(commit=False)
        form_temp.prerequisites = prerequisite
        form_temp.save()
        messages.success(request, 'Project was create successfully!')
        return redirect('ftp:admin_projects')
    context = {"form": form, 'errors': form.errors}
    return render(request, 'ftp/admin/create_project.html', context)


def profile_create(request):
    form = ProfileFormNew(request.POST or None)
    print(form.errors)
    if form.is_valid():
        form.save()
        messages.success(request, 'Profile was created successfully!')
        return redirect('ftp:admin_profiles')

    users = CustomUser.objects.all()
    context = {"form": form, 'errors': form.errors, "users": users}
    return render(request, 'ftp/admin/create_profile.html', context)


def project_delete(request, pk):
    project = get_object_or_404(Project, id=pk)
    project_name = project.project_name
    print(project.project_name)
    project.delete()
    messages.success(request, project_name + 'project was deleted successfully!')
    return redirect('ftp:admin_projects')


def profile_delete(request, pk):
    profile = get_object_or_404(Profile, id=pk)
    profile_name = profile.fullname
    profile.delete()

    messages.success(request, profile_name + 'profile was deleted successfully!')
    return redirect('ftp:admin_profiles')


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
        profile = get_object_or_404(Profile, username=request.user)
        # print(profiles)
        return render(request, 'ftp/admin/hult.html', {'allhult': hult, 'prof': profile})
    else:
        raise Http404('Page does not Exist')


def admin_professors(request):
    user = request.user

    if user.is_irc:
        professors = Professor.objects.all()
        profile = get_object_or_404(Profile, username=request.user)
        # print(profiles)
        return render(request, 'ftp/admin/professors.html', {'allprofessors': professors, 'prof': profile})
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
    fields = ['professor_name', 'university', 'project_name', 'project_detail', 'project_time', 'display', 'special',
              'deadline']
    success_url = reverse_lazy('ftp:admin_projects')

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     prereq = get_object_or_404(PreRequisite, name=context['object'].project_name)
    #     prereq.pg = self.request.POST.get('pg') or prereq.pg
    #     prereq.ug = self.request.POST.get('ug') or prereq.ug
    #     if self.request.POST.get('year') != '':
    #         prereq.year = self.request.POST.get('year')
    #
    #     if self.request.POST.get('department') != '':
    #         prereq.department = self.request.POST.get('department')
    #
    #     # context['year'] = '1'
    #
    #     print(self.request)
    #
    #     prereq.save()
    #
    #     return context

def edit_prereq(request, name):
    prereq = get_object_or_404(PreRequisite, name=name)

    if request.method == 'POST':
        prereq.pg = True if request.POST.get('pg') else False
        prereq.ug = True if request.POST.get('pg') else False
        print(prereq.ug, prereq.pg)
        if request.POST.get('year') != '':
            prereq.year = request.POST.get('year')

        if request.POST.get('department') != '':
            prereq.department = request.POST.get('department')

        prereq.save()

        return redirect(reverse_lazy('ftp:admin_projects'))
    else:
        return render(request, 'ftp/admin/edit_prereq.html', {'prereq': prereq})

def search_profile(request):
    if request.method == 'GET':
        search = request.GET.get('search')
        status = Profile.objects.filter(Q(fullname__icontains=search) | Q(
            rollno__icontains=search))  # filter returns a list so you might consider skip except part
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
    fields = ['fullname', 'department', 'contact', 'year', 'skype', 'passport', 'transcript', 'cgpa', 'cv', 'photo',
              'review', 'rollno']
    success_url = reverse_lazy('ftp:admin_profiles')


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
        project = Project.objects.create(professor_name=professor.name, university=professor.university_name,
                                         project_name=professor.project_name, project_detail=professor.project_details)
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
    project.delete()

    return render(request, 'ftp/admin/import_project.html', {'project': new_project})


def scholarship_delete(request, pk):
    scholarship = get_object_or_404(Scholarship, id=pk)

    scholarship.delete()

    return redirect("ftp:admin_scholarship")


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
    fields = ['funding_agency', 'amount', 'scholarship_name', 'scholarship_detail', 'display', 'deadline']
    success_url = reverse_lazy('ftp:admin_scholarship')


def addresult(request, pk):
    if request.method == 'POST':
        rolls = request.POST.getlist('result')
        profiles = Profile.objects.filter(rollno__in=rolls)

        proj = Project.objects.get(id=pk)
        RESULT = Result.objects.create()
        # Project=project[::1]
        RESULT.project = proj
        for profile in profiles:
            profile.selected = True
            RESULT.result.add(profile)
            profile.save()
            RESULT.save()

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

def faqs(request):
    form=faqform(request.POST or None)
    if form.is_valid():
        form.save()
        message="your feedback has been succesfully recorded!"
        return render(request,'ftp/faq.html',{'message': message})


    return render(request, 'ftp/faq.html')
