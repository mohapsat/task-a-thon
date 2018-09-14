from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Status(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Reward(models.Model):

    name = models.CharField(max_length=128)
    amount = models.SmallIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, related_name='rewards', on_delete=models.CASCADE, null=True),
    updated_by = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE, null=True)  # one sided association
    pass

    def __str__(self):
        return self.name

    def reward_display(self):
        return self.name + ' - ' + self.amount  # enhance look on dropdown


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
        return self.name

    def school_address(self):
        return self.name + ', ' + self.city + ', ' + self.state + '(' + self.zip_code + ')'


class Task(models.Model):

    name = models.CharField(max_length=50, unique=False)
    success_criteria = models.CharField(max_length=4000)
    last_updated = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateTimeField(default=datetime.now()+timedelta(days=30))  # defaulted to +30 days
    status = models.ForeignKey(Status, related_name='tasks', on_delete=models.CASCADE, null=True)
    school = models.ForeignKey(School, related_name='tasks', on_delete=models.CASCADE, null=True)
    starter = models.ForeignKey(User, related_name='tasks', on_delete=models.CASCADE, null=True)
    reward = models.ForeignKey(Reward, related_name='tasks', on_delete=models.CASCADE, null=True)
    pass

    def __str__(self):
        return self.name

    def snippet_criteria(self):
        if len(self.success_criteria) > 30:
            return self.success_criteria[:30] + '...'
        else:
            return self.success_criteria

    def snippet_name(self):
        if len(self.name) > 30:
            return self.name[:50] + '...'
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
        return self.message

    def post_snippet(self):
        if len(self.message) > 30:
            return self.message[:50] + '...'
        else:
            return self.message


# ref: https://docs.djangoproject.com/en/dev/topics/db/examples/one_to_one/
class Payment(models.Model):
    is_paid = models.BooleanField(default=False)
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    reward = models.OneToOneField(Reward, on_delete=models.CASCADE)
