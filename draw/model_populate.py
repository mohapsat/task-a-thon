from rewards.models import Status, Reward, Task, Post
from django.contrib.auth.models import User

user = User.objects.get(id=1)


Status.objects.create(name='Open')
Status.objects.create(name='Closed')
