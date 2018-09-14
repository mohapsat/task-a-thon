from django.contrib import admin

from .models import Task, Status, Reward, Post, School

# Register your models here.
admin.site.register(Task)
admin.site.register(Status)
admin.site.register(Reward)
admin.site.register(Post)
admin.site.register(School)

