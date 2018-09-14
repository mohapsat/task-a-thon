from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import UpdateView, DeleteView, ListView
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator

from .models import Task, Post, Reward, Status
from .forms import NewTaskForm, NewReplyForm


def home_view(request):
    return render(request, 'home.html')


# FBV implementation - refer to CBV below
@login_required
def tasks_view(request):
    tasks = Task.objects.all()
    # task_count = Task.objects.all().count()
    data = {'tasks': tasks}

    return render(request, 'tasks.html', data)
    # pass


'''
@login_required
class TaskListView(ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'tasks.html'
    paginated_by = 20

    def get_context_data(self, **kwargs):
        kwargs['tasks'] = self.tasks
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.tasks = get_object_or_404(Task)
        queryset = self.tasks.order_by('-last_updated').annotate(replies=Count('tasks') - 1)
        return queryset
'''


@login_required
def task_replies_view(request, pk):  # task detail view
    # task = Task.objects.get(pk=pk)
    task = get_object_or_404(Task, pk=pk)

    queryset = task.posts.order_by('-created_at').annotate(replies=Count('id'))  # posts.id
    page = request.GET.get('page', 1)

    paginator = Paginator(queryset, 4)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'task_replies.html', {"task": task, 'posts': posts})


@login_required
def new_task_view(request):  # create new task form

    # user = User.objects.first()  # TODO: get the currently logged in user
    status = Status.objects.get(name='Open')  # default Open
    reward = Reward.objects.first()           # default a reward

    if request.method == 'POST':
        form = NewTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.starter = request.user
            task.status = status
            task.reward = reward
            # task.save() # TODO: Enable after migrating , added null=True for FKs
            task = Task.objects.create(
                name=form.cleaned_data.get('name'),
                success_criteria=form.cleaned_data.get('success_criteria'),
                starter=request.user,
                status=status,
                reward=reward
            )
            return redirect('tasks')
    else:
        form = NewTaskForm()
    return render(request, 'new_task.html', {"form": form})

    pass


@login_required
def new_reply_to_task_view(request, pk):  # new reply / post to task

    task = get_object_or_404(Task, pk=pk)
    # user = User.objects.first()  # TODO: get the currently logged in user

    if request.method == 'POST':
        form = NewReplyForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.created_by = request.user
            # post.save() # TODO: Enable after migrating , added null=True for FKs
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                task=task,
                created_by=request.user
            )
            return redirect('task_replies', pk=task.pk)
    else:
        form = NewReplyForm()
    return render(request, 'new_reply_to_task.html', {"task": task, "form": form})
    pass


@login_required
def reply_to_post_view(request, pk, post_id):  # new reply to post
    task = get_object_or_404(Task, pk=pk)
    post = Task.posts.get(id=post_id)
    data = {"task": task, "post": post}

    return render(request, 'reply_to_post.html', data)
    pass


# @login_required  # decorator throws a object has no attribute 'as_view' error
@method_decorator(login_required, name='dispatch')
class TaskUpdateView(UpdateView):

    model = Task
    fields = ('name', 'success_criteria', 'expires_on', 'reward')
    template_name = 'edit_task.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'task'

    # TODO: fix for other users editing any tasks problem
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(starter=self.request.user)
        pass

    def form_valid(self, form):
        task = form.save(commit=False)
        task.updated_by = self.request.user
        task.updated_at = timezone.now()
        task.save()
        return redirect('task_replies', pk=task.pk)


@method_decorator(login_required, name='dispatch')
class TaskDeleteView(DeleteView):

    model = Task
    template_name = 'delete_task.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'task'

    def get_success_url(self):
        # task = get_object_or_404(Task, pk=self.pk)
        # return reverse_lazy('task_replies', kwargs={'pk': task.pk})
        return reverse_lazy('tasks')

    # fix for other users deleting any tasks problem
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(starter=self.request.user)
        pass

    def form_valid(self, form):
        task = form.delete()


# @login_required  # decorator throws a object has no attribute 'as_view' error
@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):

    model = Post
    fields = ('message', )
    template_name = 'edit_reply.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    # TODO: fix for other users editing any posts / replies problem
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)
        pass

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('task_replies', pk=post.task.pk)  # , post_pk=post.pk)


@method_decorator(login_required, name='dispatch')
class PostDeleteView(DeleteView):

    model = Post
    template_name = 'delete_reply.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_success_url(self):
        task = self.object.task
        return reverse_lazy('task_replies', kwargs={'pk': task.pk})

    # TODO: fix for other users deleting any posts / replies problem
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)
        pass

    def form_valid(self, form):
        post = form.delete()

