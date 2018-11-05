from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.html import escape, mark_safe
from localflavor.us.models import USStateField
from tumidpandora_school_rewards import settings
from multiselectfield import MultiSelectField


# Ref: https://simpleisbetterthancomplex.com/tutorial/2017/02/06/how-to-implement-case-insensitive-username.html
class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


# Ref: https://simpleisbetterthancomplex.com/tutorial/2018/01/18/how-to-implement-multiple-user-types-with-django.html
class User(AbstractUser):
    objects = CustomUserManager()  # for case insensitive username
    is_parent = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)


class School(models.Model):

    name = models.CharField(max_length=128)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=64)
    state = USStateField(null=True, blank=True)
    zip_code = models.CharField(max_length=32)
    paypal_account = models.CharField(max_length=128, null=True)
    is_paid = models.BooleanField(default=False)  # to check for subscription
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, related_name='schools', on_delete=models.CASCADE, null=True)
    updated_by = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE, null=True)

    # TODO: add is_premium_expiring flag to schools and throw a warning on tasks dashboard

    # class Meta:
    #     unique_together = (("city", "zip_code", "paypal_account"),)

    def __str__(self):
        # return self.name
        return "%s - %s, %s" % (self.name, self.city, self.state)


class Parent(models.Model):
    user = models.OneToOneField(User, related_name='parent', on_delete=models.CASCADE, primary_key=True)
    # school = models.ForeignKey(School, related_name='p_school', on_delete=models.CASCADE, null=True)
    school = models.ForeignKey(School, related_name='t_school', on_delete=models.CASCADE, null=True)
    is_school_admin = models.BooleanField(default=False)  # to indicate if parent is school admin

    def __str__(self):
        return "%s" % self.user

    def email_masked(self):
        return str(self.user.email)
    # TODO: Mask (not hash) user emails in my school view


class Teacher(models.Model):
    user = models.OneToOneField(User, related_name='teacher', on_delete=models.CASCADE, primary_key=True)
    school = models.ForeignKey(School, related_name='p_school', on_delete=models.CASCADE, null=True)
    # TODO: Add Grade and Room
    is_school_admin = models.BooleanField(default=False)  # to indicate if teacher is school admin

    def __str__(self):
        return "%s" % self.user


class Status(models.Model):

    OPEN = 1
    CLOSED = 2
    IN_PROGRESS = 3
    PENDING_APPROVAL = 4
    APPROVED = 5
    PENDING_PAYMENT = 6
    PAID = 7
    #
    STATUS_CHOICES = (
        (OPEN, 'Open'),
        (CLOSED, 'Closed'),
        (IN_PROGRESS, 'In Progress'),
        (PENDING_APPROVAL, 'Pending Approval'),
        (APPROVED, 'Approved'),
        (PENDING_PAYMENT, 'Pending Payment'),
        (PAID, 'Paid'),
    )

    status = models.IntegerField(default=OPEN, choices=STATUS_CHOICES, primary_key=True)
    # REF: "https://docs.djangoproject.com/en/dev/ref/models/instances/#django.db.models.Model.get_FOO_display"
    color = models.CharField(max_length=7, default='#007bff')

    def __str__(self):
        return str(self.get_status_display())

    def get_html_badge(self):

        name = escape(self.get_status_display())
        progress_percentage = 0
        if name == 'Open':
            progress_percentage = 20
            color = 'warning'
        elif name == 'In Progress':
            progress_percentage = 40
            color = 'info'
        elif name == 'Pending Approval':
            progress_percentage = 50
            color = 'primary'
        elif name == 'Pending Payment':
            progress_percentage = 80
            color = 'danger'
        else:
            progress_percentage = 100
            color = 'success'
        # color = escape(self.color)
        # html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (color, name)
        # if name != 'Open':
        #     html = '<i class="fa fa-lock text-light mr-1"></i> <span class="badge badge-info text-default">%s</span>' % name
        # else:
        #     html = '<i class="fa fa-unlock-alt text-success mr-1"></i><span class="badge badge-primary text-default">%s</span>' % name
        # html = '<span class="progress-label progress-info">%s</span>' % name

        html = '<div class="progress-wrapper"> <div class="progress-info"> <div class="progress-label"> <span class="text-default">%s</span> </div><div class="progress-percentage"><small>%s%%</small> </div></div><div class="progress"> <div class="progress-bar bg-%s" role="progressbar" aria-valuenow="%s" aria-valuemin="0" aria-valuemax="100" style="width: %s%%;"></div></div></div>' % (name, progress_percentage, color, progress_percentage, progress_percentage)
        return mark_safe(html)


class Reward(models.Model):

    name = models.CharField(max_length=128)
    amount = models.SmallIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, related_name='rewards', on_delete=models.CASCADE, null=True),
    updated_by = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE, null=True)  # one sided association
    color = models.CharField(max_length=7, default='#007bff')
    pass

    def __str__(self):
        # return self.name
        return "%s - $%s" % (self.name, self.amount)  # enhance look on dropdown

    def get_html_badge(self):
        name = escape(self.amount)
        color = escape(self.color)
        # html = '<span class="badge badge-pill badge-primary" style="background-color: %s">$%s</span>' % (color, name)
        html = '<span class="badge badge-pill badge-info">$%s</span>' % name
        return mark_safe(html)


class Task(models.Model):

    DAYS_TO_EXPIRE_TASK = 30  # default expiration date

    GRADE_CHOICES = (
        # ('ALL', 'ALL'),
        ('PS', 'PRESCHOOL'),
        ('TK', 'TK'),
        ('K', 'KINDERGARTEN'),
        ('1', 'FIRST'),
        ('2', 'SECOND'),
        ('3', 'THIRD'),
        ('4', 'FOURTH'),
        ('5', 'FIFTH'),
        ('6', 'SIXTH'),
        ('7', 'SEVENTH'),
        ('8', 'EIGHTH'),
        ('9', 'FRESHMAN'),
        ('10', 'SOPHOMORE'),
        ('11', 'JUNIOR'),
        ('12', 'SENIOR'),
    )

    name = models.CharField(max_length=125, unique=False)
    success_criteria = models.CharField(max_length=500)
    last_updated = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateTimeField(default=datetime.now()+timedelta(days=DAYS_TO_EXPIRE_TASK))  # defaulted to +30 days
    status = models.ForeignKey(Status, related_name='tasks', on_delete=models.CASCADE, null=True, default=Status.OPEN)
    school = models.ForeignKey(School, related_name='school', on_delete=models.CASCADE, null=True)
    starter = models.ForeignKey(User, related_name='tasks', on_delete=models.CASCADE, null=True)
    reward = models.ForeignKey(Reward, related_name='tasks', on_delete=models.CASCADE, null=True, default='GOLD')
    grade = MultiSelectField(choices=GRADE_CHOICES, max_choices=6, max_length=64)


    # TODO: Remove default reward hard coding
    pass

    def __str__(self):
        return self.name[:10]

    def grade_display(self):
        return str(self.get_grade_display())

    def snippet_criteria(self):
        if len(self.success_criteria) > 30:
            return self.success_criteria[:30] + '...'
        else:
            return self.success_criteria

    def snippet_name(self):
        if len(self.name) > 30:
            return self.name[:30] + '...'
        else:
            return self.name

    def is_expired(self):
        # self.expires_on returns a datetime.datetime object, converting to date
        return self.expires_on.date() < datetime.now().date()

    def avatar_text(self):
        return "%s%s" % (self.starter.first_name[:1], self.starter.last_name[:1])


class Post(models.Model):

    message = models.CharField(max_length=480)
    task = models.ForeignKey(Task, related_name='posts', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE, null=True)
    updated_by = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE, null=True)  # one sided association
    pass

    def __str__(self):
        return self.message[:50]

    def post_snippet(self):
        if len(self.message) > 30:
            return self.message[:50] + '...'
        else:
            return self.message


# ref: https://docs.djangoproject.com/en/dev/topics/db/examples/one_to_one/
# class Payment(models.Model):
#     is_paid = models.BooleanField(default=False)
#     task = models.OneToOneField(Task, on_delete=models.CASCADE)
#     reward = models.OneToOneField(Reward, on_delete=models.CASCADE)


class Claim(models.Model):

    message = models.CharField(max_length=400, null=False)
    status = models.ForeignKey(Status, related_name='claims', on_delete=models.CASCADE, null=True, default=Status.OPEN)
    task = models.ForeignKey(Task, related_name='claims', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, related_name='claims', on_delete=models.CASCADE, null=True)
    updated_by = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE, null=True)
    approved_by = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE, null=True)
    approved_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message[:30]

    def message_snippet(self):
        if len(self.message) >= 50:
            return self.message[:50]+'...'
        else:
            return self.message


class Payment(models.Model):

    # status = models.ForeignKey(Status, related_name='payments', on_delete=models.CASCADE, null=True, default=Status.OPEN)
    # payment status is not needed, using task status.. all payments are paid
    task = models.ForeignKey(Task, related_name='payments', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='payments', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.task


class UpgradeCharge(models.Model):

    charge_success = models.BooleanField(default=False)
    amount = models.IntegerField(default=settings.STRIPE_PREMIUM_CHARGE)
    school = models.ForeignKey(School, related_name='upgradeCharges', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='upgradeCharges', on_delete=models.CASCADE, null=True)
    charge_id = models.CharField(max_length=256, null=True)  # to store stripe_charge_id

    def __str__(self):
        return "%s" % self.charge_id
