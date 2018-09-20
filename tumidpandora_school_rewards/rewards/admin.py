from django.contrib import admin

from .models import Task, Status, Reward, Post, School, Claim, User, Parent, Teacher

# Register your models here.
admin.site.register(Task)
admin.site.register(Status)
admin.site.register(Reward)
admin.site.register(Post)
admin.site.register(School)
admin.site.register(Claim)
admin.site.register(User)
admin.site.register(Parent)
admin.site.register(Teacher)
