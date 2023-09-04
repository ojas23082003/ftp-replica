# Create your models here.
# from django.contrib.auth.models import Permission
from django.utils import timezone
from pickle import FALSE
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
Proj_mode = (
    ('On-site', 'On-site'),
    ('Remote', 'Remote')
)
Degree_type = (
    ('UG', 'UG'),
    ('PG', 'PG')
)

COLOR_STATUS = (
    ('Pending', 'PENDING'),
    ('Shortlisted For Interview', 'SHORTLISTED FOR INTERVIEW'),
    ('Selected', 'SELECTED'),
    ('Rejected', 'REJECTED'),
    ('Not Selected', 'NOT SELECTED')
)


class CustomUser(AbstractUser):
    is_student = models.BooleanField(default=True)
    is_irc = models.BooleanField(default=False)


class Profile(models.Model):
    username = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    fullname = models.CharField(max_length=250, null=True)
    department = models.CharField(max_length=99, null=True)
    contact = models.CharField(max_length=29, null=True)
    year = models.CharField(max_length=30, null=True)
    degree_type = models.CharField(max_length=30, choices=Degree_type, default="UG")
    alt_email = models.CharField(max_length=250, null=True)
    passport = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    transcript = models.FileField(null=True, blank=True)
    cgpa = models.CharField(max_length=29, null=True)
    cv = models.FileField(null=True, blank=True)
    photo = models.FileField(null=True, blank=True)
    review = models.CharField(max_length=30, null=True, blank=True)
    rollno = models.CharField(max_length=10, null=True)
    selected = models.BooleanField(default=False)
    updated = models.BooleanField(default=False)
    viewedNotifications = models.TextField(default=",", max_length=5000)
    # requestedTopic = models.ForeignKey(
    #     RequestedTopic, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-username__is_irc']

    def __str__(self):
        return str(self.username) + str(' | ') + self.fullname


class TopicManager(models.Manager):

    def get_queryset(self):
        query = super().get_queryset().filter(
            verified=False,
            created_at__gte=timezone.now()-timezone.timedelta(days=7)
        ) | super().get_queryset().filter(
            verified=True)
        return query


class RequestedTopic(models.Model):
    topicName = models.CharField(max_length=250, null=True)
    count = models.IntegerField(default=0)
    users = models.ManyToManyField(Profile, related_name='topics',
                                   null=True, blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = TopicManager()

    def __str__(self):
        return str(self.topicName)

# @receiver(post_save, sender=CustomUser)
# def update_user_profile(sender, instance, created]):
# if created:
# Profile.objects.create(user=instance)
# instance.profile.save()


class PreRequisite(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    detail = models.TextField(max_length=5000, null=True)
    pg = models.BooleanField(default=False)
    ug = models.BooleanField(default=False)
    year = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=200, null=True, blank=True)
    deadline = models.BooleanField(default=False)

    # More pre-requisites can be added

    def __str__(self):
        return str(self.name)


class ProjectTag(models.Model):
    # tag_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # TAGs = {}
    title = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return str(self.title)


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ManyToManyField(Profile, through='Application', through_fields=('project', 'profile'),
                                     related_name="project", blank=True)
    professor_name = models.CharField(max_length=250, null=True)
    university = models.CharField(max_length=500, null=True)
    project_name = models.CharField(max_length=500, null=True)
    project_detail = models.TextField(max_length=5000, null=True)
    project_mode = models.CharField(
        max_length=30, choices=Proj_mode, default="Remote")
    project_time = models.CharField(max_length=100, null=True)
    project_image = models.FileField(null=True, blank=True, upload_to='projects')
    display = models.BooleanField(default=False)
    special = models.BooleanField(default=False)
    deadline = models.DateField(null=True)
    multi_domain = models.BooleanField(default=False)
    bookmarks = models.ManyToManyField(
        Profile, related_name='bookmarks', blank=True)
    prerequisite = models.OneToOneField(
        PreRequisite, on_delete=models.CASCADE, related_name='prof_prerequisites', null=True, blank=True)
    reason = models.CharField(max_length=100, null=True, blank=True)
    stipend = models.CharField(max_length=100, null=True)
    currency = models.CharField(max_length=100, null=True)

    # TAGs = {}
    # tags = models.CharField(max_length=50, null=True, blank=True, choices=TAGs)
    tags = models.ManyToManyField(ProjectTag, related_name='tags', blank=True)

    def __str__(self):
        return str(self.project_name)+"   " + str(self.id)


class ProjectDomain(models.Model):
    name = models.CharField(max_length=200, null=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class Scholarship(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ManyToManyField(Profile, through='Scholarship_appli', through_fields=(
        'scholarship', 'profile'), related_name="scholarship")
    funding_agency = models.CharField(max_length=250, null=True)
    amount = models.CharField(max_length=500, null=True)
    scholarship_name = models.CharField(max_length=500, null=True)
    scholarship_detail = models.TextField(max_length=5000, null=True)
    display = models.BooleanField(default=False)
    deadline = models.DateField(null=True)
    bookmarks = models.ManyToManyField(
        Profile, related_name='bookmarkss', blank=True)
    link = models.TextField(max_length=5000, null=True, blank=True)

    #TAGs = {}
    #tags = models.CharField(max_length=50, null=True, blank=True, choices=TAGs)

    def __str__(self):
        return str(self.scholarship_name)+"   " + str(self.id)


class Application(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, null=True, blank=True)
    project_domain1 = models.CharField(max_length=200, null=True, blank=True)
    project_domain2 = models.CharField(max_length=200, null=True, blank=True)
    project_domain3 = models.CharField(max_length=200, null=True, blank=True)
    sop = models.TextField(max_length=50000, null=True)
    Loi = models.TextField(max_length=50000, null=True, blank=True)
    ncv = models.FileField(null=True, blank=True)
    noc = models.FileField(null=True, blank=True)
    reviewed = models.BooleanField(default=True)
    status = models.CharField(
        max_length=30, choices=COLOR_STATUS, default='Pending')
    reviewed_by = models.CharField(max_length=250, null=True)
    display_prof = models.BooleanField(default=True)

    # priority = models.CharField(max_length=1, choices=PRIOTITIES, null=True, default='10')
    # PRIOTITIES = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
    # ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'),
    # ('18', '18'), ('19', '19'), ('20', '20'))

    def __str__(self):
        return str(self.profile.fullname) + str(' | ') + str(self.project.project_name) + str(' | ') + str(self.status)


class Scholarship_appli(models.Model):
    scholarship = models.ForeignKey(
        Scholarship, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=250, null=True)
    roll = models.CharField(max_length=250, null=True)
    email = models.CharField(max_length=250, null=True)
    department = models.CharField(max_length=250, null=True)
    yearOfGrad = models.CharField(max_length=250, null=True)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, null=True, blank=True)
    NameofFacultyAdvisor = models.TextField(max_length=50000, null=True)
    NameofHOD = models.TextField(max_length=50000, null=True)
    Nameofhostinstitution = models.CharField(max_length=1000, null=True)
    DetailsOfTheProposedResearch_or_professionalInternship = models.CharField(
        max_length=5500, null=True)
    sop = models.CharField(max_length=5500, null=True)
    HistoryOfCollobration = models.CharField(
        max_length=10000, null=True, blank=True)
    DurationOfVisit_from = models.CharField(max_length=1000, null=True)
    DurationOfVisit_to = models.CharField(max_length=1000, null=True)
    Justification_of_applying_through_the_IITKGF_Of_USA_AwardProgram = models.CharField(
        max_length=10000, null=True)
    PossibleOutcomeOfYourProposedResearch = models.CharField(
        max_length=10000, null=True)
    Explain_in_about_250_words_how_your_engagement_with_the_Host_Institute = models.CharField(
        max_length=10000, null=True)
    cv = models.FileField(null=True)
    Awards = models.FileField(null=True, blank=True)
    Transcript = models.FileField(null=True)
    NOC = models.FileField(null=True)
    letter_of_endorsement = models.FileField(null=True, blank=True)
    work_publication = models.FileField(null=True, blank=True)
    fuding_proof = models.FileField(null=True, blank=True)
    offer_letter = models.FileField(null=True)
    reviewed = models.BooleanField(default=False)
    display = models.BooleanField(default=False)
    reviewed_by = models.CharField(max_length=250, null=True, blank=True)
    # use ForeignKey.limitchoiceto and check is_staff==true (https://docs.djangoproject.com/en/2.1/ref/models/fields/#django.db.models.ForeignKey.limit_choices_to)

    # priority = models.CharField(max_length=1, choices=PRIOTITIES, null=True, default='10')
    # PRIOTITIES = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
    # ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'),
    # ('18', '18'), ('19', '19'), ('20', '20'))

    def __str__(self):
        if self.profile is not None:
            return str(self.profile.fullname) + " | " + str(self.scholarship.scholarship_name)
        else:
            return str(self.scholarship.scholarship_name)


class gkf_appli(models.Model):
    name = models.CharField(max_length=250, null=True)
    roll = models.CharField(max_length=250, null=True)
    email = models.CharField(max_length=250, null=True)
    contact = models.CharField(max_length=250, null=True)
    student = models.CharField(max_length=250, null=True)
    yearOfStudy = models.CharField(max_length=250, null=True)
    department = models.CharField(max_length=250, null=True)
    cgpa = models.CharField(max_length=250, null=True)
    transcript = models.FileField(null=True)
    cv = models.FileField(null=True)
    sop = models.TextField(max_length=5500, null=True)
    type = models.CharField(max_length=250, null=True)
    offer_letter = models.FileField(null=True)
    self_declaration = models.FileField(null=True)
    noc = models.FileField(null=True)
    durationOfVisit_from = models.CharField(max_length=1000, null=True)
    durationOfVisit_to = models.CharField(max_length=1000, null=True)
    hostUniversity = models.CharField(max_length=1000, null=True)
    previously_funded = models.BooleanField(default=False)
    funding_proof = models.FileField(null=True, blank=True)

    def __str__(self):
        return str(self.name)

class scholarship2k23_appli(models.Model):
    # contact = models.CharField(max_length=250, null=True)
    # student = models.CharField(max_length=250, null=True)
    # department = models.CharField(max_length=250, null=True)
    # cv = models.FileField(null=True)
    # sop = models.TextField(max_length=5500, null=True)
    # type = models.CharField(max_length=250, null=True)
    name = models.CharField(max_length=250, null=True)
    roll = models.CharField(max_length=250, null=True)
    email = models.CharField(max_length=250, null=True)
    yearOfStudy = models.CharField(max_length=250, null=True)
    cgpa = models.CharField(max_length=250, null=True)
    transcript = models.FileField(null=True)
    hasBacklog = models.BooleanField(default=False)
    applying_to = models.CharField(max_length=250, null=True)
    offer_letter = models.FileField(null=True)
    hostUniversity = models.CharField(max_length=1000, null=True)
    mode = models.CharField(max_length=100, null=True)
    durationOfVisit_from = models.CharField(max_length=1000, null=True)
    durationOfVisit_to = models.CharField(max_length=1000, null=True)
    noc = models.FileField(null=True)
    lor = models.FileField(null=True)
    previously_funded = models.BooleanField(default=False)
    funding_proof = models.FileField(null=True, blank=True)
    project_desc = models.TextField(max_length=5500, null=True)
    # self_declaration = models.FileField(null=True)

    def __str__(self):
        return str(self.name)


class Result(models.Model):
    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, null=True, blank=True)
    result = models.ManyToManyField(
        Profile, related_name='Resultss', blank=True)

    def __str__(self):
        return str(self.project)


class Professor(models.Model):
    name = models.CharField(max_length=250, null=True)
    # email = models.EmailField(max_length=250, null=True, )
    university_name = models.CharField(max_length=99, null=True)
    project_name = models.CharField(max_length=200, null=True)
    project_details = models.TextField(max_length=5000, null=True)
    no_of_students = models.CharField(max_length=400, null=True)
    prerequisites = models.TextField(max_length=5000, null=True)
    duration = models.CharField(max_length=100, null=True)
    stipend = models.CharField(max_length=100, null=True)
    currency = models.CharField(max_length=100, null=True)
    target = models.CharField(max_length=100, null=True)
    per = models.CharField(max_length=100, null=True)
    mode = models.CharField(max_length=100, null=True)
    skype = models.CharField(max_length=100, null=True)
    imported = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)


class Dyuti(models.Model):
    first_name = models.CharField(max_length=250, null=True)
    last_name = models.CharField(max_length=250, null=True)
    phone = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=100, null=True)
    gender = models.CharField(max_length=20, null=True)
    country = models.CharField(max_length=500, null=True)
    student_photo = models.FileField(null=True, blank=True)
    # uni_home = models.CharField(max_length=250, null=True)

    passport_no = models.CharField(max_length=250, null=True)
    visa_no = models.CharField(max_length=250, null=True)
    visa_cate = models.CharField(max_length=250, null=True)
    visa_validity = models.DateField(("Date"), blank=True, null=True)
    passport_ID = models.FileField(null=True, blank=True)
    visa_page = models.FileField(null=True, blank=True)

    uni_india = models.CharField(max_length=500, null=True)
    state = models.CharField(max_length=250, null=True)
    city = models.CharField(max_length=250, null=True)
    department = models.CharField(max_length=200, null=True)
    year_of_study = models.CharField(max_length=50, null=True)
    reg_no = models.CharField(max_length=250, null=True)
    reg_ID = models.FileField(null=True, blank=True)
    # degree = models.CharField(max_length=50, null=True, choices=(
    # ('UG', 'UG'), ('PG', 'PG'), ('PhD', 'PhD'), ('Short Term', 'Short Term')))  # UG/PG/PhD

    is_scholarship = models.CharField(max_length=100, null=True)
    comments = models.TextField(max_length=2000, null=True, blank=True)

    # is_interested = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.first_name) + str('|') + str(self.country)


# class Hult(models.Model):
#     team_name = models.CharField(max_length=250, null=True)
#     leader_name = models.CharField(max_length=250, null=True)
#     email_leader = models.EmailField(max_length=100, null=True)
#     member_2 = models.CharField(max_length=250, null=True)
#     email_mem2 = models.EmailField(max_length=100, null=True)
#     member_3 = models.CharField(max_length=250, null=True)
#     email_mem3 = models.EmailField(max_length=100, null=True)
#     member_4 = models.CharField(max_length=250, null=True, blank=True)
#     email_mem4 = models.EmailField(max_length=100, null=True, blank=True)
#     queries = models.CharField(max_length=1000, null=True, blank=True)

#     def __str__(self):
#         return str(self.team_name)

class Hult(models.Model):
    team_name = models.CharField(max_length=250, null=True)
    leader_name = models.CharField(max_length=250, null=True)
    email_leader = models.EmailField(max_length=100, null=True)
    contact_leader = models.CharField(max_length=29, null=True)
    report = models.FileField(null=True, blank=True)
    offline_mode_of_hult = models.BooleanField(default=False)

    def __str__(self):
        return str(self.team_name)


class FeedBack_PROF(models.Model):
    professor_name = models.CharField(max_length=200, null=True)
    university_name = models.CharField(max_length=200, null=True)
    student_name = models.CharField(max_length=200, null=True)
    passionate_marks = models.CharField(max_length=10, null=True)
    satisfaction_marks = models.CharField(max_length=10, null=True)
    ethics_marks = models.CharField(max_length=10, null=True)
    creative_marks = models.CharField(max_length=10, null=True)
    overall_marks = models.CharField(max_length=10, null=True)
    suggestions = models.CharField(max_length=1000, null=True)
    feedback = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return str(self.professor_name + ' | ' + self.university_name + ' | ' + self.student_name)


class FeedBack_stu(models.Model):
    professor_name = models.CharField(max_length=200, null=True)
    Professor_email = models.CharField(max_length=200, null=True)
    university_name = models.CharField(max_length=200, null=True)
    student_name = models.CharField(max_length=200, null=True)
    relevant_work = models.CharField(max_length=200, null=True)
    supportive = models.CharField(max_length=10, null=True)
    satisfied = models.CharField(max_length=10, null=True)
    rate_marks = models.CharField(max_length=10, null=True)
    interview = models.CharField(max_length=1000, null=True)
    feedback = models.CharField(max_length=1000, null=True)

    suggestions = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return str(self.student_name + '|' + self.professor_name + ' | ' + self.university_name)


class Notice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=5000, blank=True, null=True)
    date = models.DateField(null=True)
    is_important = models.BooleanField(default=False)

    def __str__(self):
        return str(self.title)


class Anu(models.Model):
    fullname = models.CharField(max_length=250, null=True)
    rollno = models.CharField(max_length=10, null=True)
    email = models.CharField(max_length=250, null=True)
    year = models.CharField(max_length=30, null=True)
    contact = models.CharField(max_length=29, null=True)
    sop = models.CharField(max_length=5000, null=True)
    lor1 = models.FileField(null=True, blank=True)
    lor2 = models.FileField(null=True, blank=True)
    undertaking = models.FileField(null=True, blank=True)
    cv = models.FileField(null=True, blank=True)
    transcript = models.FileField(null=True, blank=True)
    pref1 = models.CharField(max_length=1000, null=True, blank=True)
    pref2 = models.CharField(max_length=1000, null=True, blank=True)
    pref3 = models.CharField(max_length=1000, null=True, blank=True)
    former_anu = models.BooleanField(default=False)

    def __str__(self):
        return str(self.fullname)


class EPFL(models.Model):
    email = models.CharField(max_length=250, null=True)
    fullname = models.CharField(max_length=250, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    dob = models.CharField(max_length=10, null=True)
    start = models.CharField(max_length=10, null=True)
    end = models.CharField(max_length=10, null=True)
    year = models.CharField(max_length=30, null=True)
    programme = models.CharField(max_length=99, null=True)
    duration = models.IntegerField(default=4)
    cgpa = models.CharField(max_length=29, null=True)
    duration = models.CharField(max_length=29, null=True)
    sop = models.FileField(null=True, blank=True)
    cv = models.FileField(null=True, blank=True)
    transcript = models.FileField(null=True, blank=True)
    pref1 = models.CharField(max_length=1000, null=True)
    pref2 = models.CharField(max_length=1000, null=True)
    pref3 = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return str(self.fullname)


class Anu_2022(models.Model):
    fullname = models.CharField(max_length=250, null=True)
    rollno = models.CharField(max_length=10, null=True)
    email = models.CharField(max_length=250, null=True)
    year = models.CharField(max_length=30, null=True)
    contact = models.CharField(max_length=29, null=True)
    sop = models.CharField(max_length=5000, null=True)
    lor1 = models.FileField(null=True, blank=True)
    lor2 = models.FileField(null=True, blank=True)
    undertaking = models.FileField(null=True, blank=True)
    cv = models.FileField(null=True, blank=True)
    transcript = models.FileField(null=True, blank=True)
    pref1 = models.CharField(max_length=1000, null=True, blank=True)
    pref2 = models.CharField(max_length=1000, null=True, blank=True)
    pref3 = models.CharField(max_length=1000, null=True, blank=True)
    former_anu = models.BooleanField(default=False)

    def __str__(self):
        return str(self.fullname)


class SAIP(models.Model):
    fullname = models.CharField(max_length=250, null=True)
    rollno = models.CharField(max_length=10, null=True)
    email = models.CharField(max_length=250, null=True)
    # institute_email = models.CharField(max_length=250, null=True)
    # contact = models.CharField(max_length=29, null=True)
    query = models.CharField(max_length=500, null=True, blank=True)
    mode_of_saip = models.BooleanField(default=False)

    def __str__(self):
        return str(self.fullname)

class Noticeboard(models.Model):
    topic = models.CharField(max_length=250, default="")
    date = models.DateField(null=True)
    image = models.FileField(null=True, blank=True)
    description = models.TextField(max_length=2000,default="")
    is_visible = models.BooleanField(default=False)

    def __str__(self):
        return str(self.topic)

class Event(models.Model):
    title = models.CharField(max_length=250,default="")
    date = models.DateField(null=True)
    description = models.TextField(max_length=2000,default="")
    img = models.FileField(null=True, blank=True)
    display = models.BooleanField(default=False)
    def __str__(self):
        return str(self.title)

class EventImage(models.Model):
    title = models.CharField(max_length=250, default="")
    image = models.FileField(null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return str(self.title)

class Type(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return (self.name)

class Year(models.Model):
    year = models.IntegerField()

    def __str__(self):
        return (str(self.year))

class Testimonials(models.Model):
    title = models.CharField(max_length=250)
    subTitle = models.CharField(max_length=250)
    content = models.TextField()
    type = models.ForeignKey(Type, on_delete=models.CASCADE, null=True, blank=True)
    year = models.ForeignKey(Year, on_delete=models.CASCADE, null=True, blank=True)
    image = models.FileField(null=True, blank=True)
    display = models.BooleanField(default=False)

    def __str__(self):
        return (self.title)

class Team(models.Model):
    title = models.CharField(max_length=250)
    sub_title = models.CharField(max_length=250)
    linkedin_link = models.URLField(max_length=300)
    facebook_link = models.URLField(max_length=300)
    email_link = models.URLField(max_length=300)
    image = models.FileField(null=True, blank=True)
    year = models.ForeignKey(Year, on_delete=models.CASCADE, null=True, blank=True)
    display = models.BooleanField(default=False)

    def __str__(self):
        return (self.title)

# class InfoTitle(models.Model):
#     title = models.CharField(max_length=250)

#     def __str__(self):
#         return (self.title)

class HultInfo(models.Model):
    title = models.CharField(max_length=250)
    subtitle = models.CharField(max_length=250,null=True, blank=True)
    desc = models.TextField()
    links = models.BooleanField(default=False)

    def __str__(self):
        return (self.title)

class HultPoster(models.Model):
    title = models.CharField(max_length=250)
    image = models.ImageField(null=True, blank=True)
    link = models.URLField()

    def __str__(self):
        return (self.title)

class InfoLink(models.Model):
    title = models.CharField(max_length=250)
    subtitle = models.CharField(max_length=250)
    link = models.URLField()

    def __str__(self):
        return (self.subtitle)