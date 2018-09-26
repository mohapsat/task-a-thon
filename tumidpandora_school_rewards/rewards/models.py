from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.html import escape, mark_safe


# Ref: https://simpleisbetterthancomplex.com/tutorial/2018/01/18/how-to-implement-multiple-user-types-with-django.html
class User(AbstractUser):
    is_parent = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)


class School(models.Model):

    name = models.CharField(max_length=64)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=25)
    zip_code = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, related_name='schools', on_delete=models.CASCADE, null=True)
    updated_by = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE, null=True)

    def __str__(self):
        # return self.name
        return "%s - %s, %s" % (self.name, self.city, self.state)


class Parent(models.Model):
    user = models.OneToOneField(User, related_name='parent', on_delete=models.CASCADE, primary_key=True)
    # school = models.ForeignKey(School, related_name='p_school', on_delete=models.CASCADE, null=True)
    school = models.ForeignKey(School, related_name='t_school', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "%s" % self.user


class Teacher(models.Model):
    user = models.OneToOneField(User, related_name='teacher', on_delete=models.CASCADE, primary_key=True)
    # school = models.ForeignKey(School, related_name='t_school', on_delete=models.CASCADE, null=True)
    # TODO: Add Grade and Room
    school = models.ForeignKey(School, related_name='p_school', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "%s" % self.user


class Status(models.Model):

    OPEN = 1
    CLOSED = 2
    IN_PROGRESS = 3
    PENDING_APPROVAL = 4
    APPROVED = 5
    CLOSED = 6
    PENDING_PAYMENT = 7
    #
    STATUS_CHOICES = (
        (OPEN, 'Open'),
        (CLOSED, 'Closed'),
        (IN_PROGRESS, 'In Progress'),
        (PENDING_APPROVAL, 'Pending Approval'),
        (APPROVED, 'Approved'),
        (PENDING_PAYMENT, 'Pending Payment'),
    )

    status = models.IntegerField(default=OPEN, choices=STATUS_CHOICES, primary_key=True)
    # REF: "https://docs.djangoproject.com/en/dev/ref/models/instances/#django.db.models.Model.get_FOO_display"
    color = models.CharField(max_length=7, default='#007bff')

    def __str__(self):
        return str(self.get_status_display())

    def get_html_badge(self):
        name = escape(self.get_status_display())
        color = escape(self.color)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (color, name)
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
        html = '<span class="badge badge-pill badge-primary" style="background-color: %s">$%s</span>' % (color, name)
        return mark_safe(html)


class Task(models.Model):

    DAYS_TO_EXPIRE_TASK = 30  # default expiration date

    name = models.CharField(max_length=50, unique=False)
    success_criteria = models.CharField(max_length=4000)
    last_updated = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateTimeField(default=datetime.now()+timedelta(days=DAYS_TO_EXPIRE_TASK))  # defaulted to +30 days
    status = models.ForeignKey(Status, related_name='tasks', on_delete=models.CASCADE, null=True, default=Status.OPEN)
    school = models.ForeignKey(School, related_name='school', on_delete=models.CASCADE, null=True)
    starter = models.ForeignKey(User, related_name='tasks', on_delete=models.CASCADE, null=True)
    reward = models.ForeignKey(Reward, related_name='tasks', on_delete=models.CASCADE, null=True, default='GOLD')
    # TODO: Remove default reward hard coding
    pass

    def __str__(self):
        return self.name[:10]

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


class Post(models.Model):

    message = models.CharField(max_length=4000)
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

    message = models.CharField(max_length=4000, null=False)
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
