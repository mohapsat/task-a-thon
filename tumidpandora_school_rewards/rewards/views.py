from django.db.models import Count, Q, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

# from django.contrib.auth.models import User

from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.views.generic import UpdateView, DeleteView, ListView
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator

from .models import Task, Post, Reward, Status, Claim, Parent, Teacher, User
from .forms import NewTaskForm, NewReplyForm, NewClaimForm, ClaimApprovalForm


from django.core.exceptions import ObjectDoesNotExist

import json


def home_view(request):
    return render(request, 'home.html')


# FnBasedVw implementation - refer to ClsBsdVw below
@login_required
def tasks_view(request):

    # TODO: Determine if view is the best place to filter tasks or pass all tasks and schools to template
    try:
        if request.user.is_parent:
            school = request.user.parent.school
        else:
            school = request.user.teacher.school
    except ObjectDoesNotExist:
        school = None  # TODO: Admin should see tasks for all schools

    # TODO: Filter tasks by school - DONE.
    tasks = Task.objects.filter(school=school).order_by('-last_updated')

    page = request.GET.get('page', 1)

    paginator = Paginator(tasks, 50)

    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)

# section for chart
    # chart_dataset = Task.objects.\
    #     values('status').\
    #     annotate(open_count=Count('status', filter(Q(status=1))))

    # Get status and count of tasks for logged in user's school

    # TODO: For pie to work, it needs {name:, y:} for series data

    # REF: https://simpleisbetterthancomplex.com/tutorial/2016/12/06/how-to-create-group-by-queries.html
    chart_left_data = Task.objects.filter(school=school).values('reward__name').annotate(Sum('reward__amount'))
    chart_left_categories = list()
    chart_left_counts_series = list()

    # print("chart_left_data = %s" % chart_left_data)

    for entry in chart_left_data:
        chart_left_categories.append(entry['reward__name'])
        chart_left_counts_series.append({'name': entry['reward__name'], 'y': entry['reward__amount__sum']})

    # print("chart_left_categories = %s" % chart_left_categories)
    # print("chart_left_counts_series = %s" % chart_left_counts_series)

    chart_left_counts_series = {
        'name': 'Rewards',
        'colorByPoint': 'true',
        'data': chart_left_counts_series
    }

    chart_left = {
        'chart': {'type': 'pie'},  # column, pie, area, line
        'title': {'text': '$ Rewards'},
        'tooltip': {
            'pointFormat': '{series.name}: <b>${point.y}</b>'
        },
        'plotOptions': {
            'pie': {
                'cursor': 'pointer',
                'allowPointSelect': 'true',
                'dataLabels': {
                    'enabled': 'true',
                    'format': '<b>{point.name}</b>: ${point.y}'
                },
                'style': {
                    'color': "(Highcharts.theme & & Highcharts.theme.contrastTextColor) | | 'black'"
                }
            }
        },
        'xAxis': {'categories': chart_left_categories},
        'series': [chart_left_counts_series]
    }

    chart_middle_data = Task.objects.filter(school=school).values('status')\
        .annotate(Count('id'))

    chart_middle_categories = list()
    chart_middle_counts_series = list()
    # print("chart_middle_data = %s" % chart_middle_data)

    # STATUS_CHOICES = (
    #     (OPEN, 'Open'),
    #     (CLOSED, 'Closed'),
    #     (IN_PROGRESS, 'In Progress'),
    #     (PENDING_APPROVAL, 'Pending Approval'),
    #     (APPROVED, 'Approved'),
    #     (PENDING_PAYMENT, 'Pending Payment'),
    # )

    for entry in chart_middle_data:

        if entry['status'] == 1:
            entry['status'] = 'Open'
        elif entry['status'] == 2:
            entry['status'] = 'Closed'
        elif entry['status'] == 3:
            entry['status'] = 'In Progress'
        elif entry['status'] == 4:
            entry['status'] = 'Pending Approval'
        elif entry['status'] == 5:
            entry['status'] = 'Approved'
        elif entry['status'] == 6:
            entry['status'] = 'Pending Payment'

        chart_middle_categories.append(entry['status'])
        chart_middle_counts_series.append({'name': entry['status'], 'y': entry['id__count']})

    # print("chart_middle_categories = %s" % chart_middle_categories)

    chart_middle_counts_series = {
        'name': 'Tasks',
        'colorByPoint': 'true',
        'data': chart_middle_counts_series
    }

    chart_middle = {
        'chart': {'type': 'bar'},  # column, pie, area, line
        'title': {'text': '# Task Statuses'},
        'tooltip': {
            'pointFormat': '{series.name}: <b>{point.y}</b>'
        },
        'plotOptions': {
            'bar': {
                'cursor': 'pointer',
                'allowPointSelect': 'true',
                'dataLabels': {
                    'enabled': 'true',
                    'format': '{point.y}'
                },
                'style': {
                    'color': "(Highcharts.theme & & Highcharts.theme.contrastTextColor) | | 'black'"
                }
            }
        },
        'xAxis': {'categories': chart_middle_categories},
        'series': [chart_middle_counts_series]
    }

    # chart_right_data = chart_left_data
    chart_right_data = Task.objects.filter(school=school). \
        filter(claims__status__in=[4, 5]).\
        values('claims__status').annotate(Count('id'))
    chart_right_categories = list()
    chart_right_counts_series = list()

    # print("chart_right_data = %s" % chart_right_data)

    for entry in chart_right_data:

        # if entry['claims__status'] == 1:
        #     entry['claims__status'] = 'Open'
        # elif entry['claims__status'] == 2:
        #     entry['claims__status'] = 'Closed'
        # elif entry['claims__status'] == 3:
        #     entry['claims__status'] = 'In Progress'
        if entry['claims__status'] == 4:
            entry['claims__status'] = 'Pending Approval'
        elif entry['claims__status'] == 5:
            entry['claims__status'] = 'Approved'
        # elif entry['claims__status'] == 6:
        #     entry['claims__status'] = 'Pending Payment'

        chart_right_categories.append(entry['claims__status'])
        chart_right_counts_series.append({'name': entry['claims__status'],'y': entry['id__count']})

    chart_right_counts_series = {
        'name': 'Claims',
        'colorByPoint': 'true',
        'data': chart_right_counts_series
    }

    # print("chart_right_counts_series = %s" % chart_right_counts_series)

    chart_right = {
        'chart': {'type': 'column'},  # column, pie, area, line
        'title': {'text': '# Reward Claims'},
        'tooltip': {
            'pointFormat': '{series.name}: <b>{point.y}</b>'
        },
        'plotOptions': {
            'column': {
                'cursor': 'pointer',
                'allowPointSelect': 'true',
                'dataLabels': {
                    'enabled': 'true',
                    'format': '{point.y}'
                },
                'style': {
                    'color': "(Highcharts.theme & & Highcharts.theme.contrastTextColor) | | 'black'"
                }
            }
        },
        'xAxis': {'categories': chart_right_categories},
        'series': [chart_right_counts_series]
    }

    dump_left = json.dumps(chart_left)
    dump_middle = json.dumps(chart_middle)
    dump_right = json.dumps(chart_right)

    return render(request, 'tasks.html', {'tasks': tasks, 'school': school,
                                          'chart_left': dump_left,
                                          'chart_middle': dump_middle,
                                          'chart_right': dump_right
                                          })
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
    # claims = get_list_or_404(Claim)

    try:
        # claims = Claim.objects.get(task=task)
        claims = Claim.objects.filter(task=task)  # .values()
    except ObjectDoesNotExist:
        claims = None

    # TODO: Determine if view is the best place to filter tasks or pass all tasks and schools to template
    try:
        if request.user.is_parent:
            school = request.user.parent.school
        else:
            school = request.user.teacher.school
    except ObjectDoesNotExist:
        school = None  # TODO: Admin should see tasks for all schools

    queryset = task.posts.order_by('-created_at').annotate(replies=Count('id'))  # posts.id

    page = request.GET.get('page', 1)

    paginator = Paginator(queryset, 2)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'task_replies.html', {"task": task, 'posts': posts,
                                                 'claims': claims, 'school': school})


@login_required
def new_task_view(request):  # create new task form

    # user = User.objects.first()  # TODO: get the currently logged in user
    status = get_object_or_404(Status, status=Status.OPEN)  # default Open
    # reward = Reward.objects.first()  # default a reward

    try:
        if request.user.is_parent:
            school = request.user.parent.school
        else:
            school = request.user.teacher.school
    except ObjectDoesNotExist:
        school = None  # TODO: Admin should see tasks for all schools

    if request.method == 'POST':
        form = NewTaskForm(request.POST)
        reward = Reward.objects.get(id=request.POST['reward'])  # Get reward from select field
        if form.is_valid():
            task = form.save(commit=False)
            task.starter = request.user
            task.status = status  # Set new task status to Open
            task.reward = reward
            # task.save() # TODO: Enable after migrating , added null=True for FKs
            task = Task.objects.create(
                name=form.cleaned_data.get('name'),
                success_criteria=form.cleaned_data.get('success_criteria'),
                starter=request.user,
                school=school,
                status=status,
                reward=reward
            )
            return redirect('tasks')
    else:
        form = NewTaskForm()
    return render(request, 'new_task.html', {"form": form, "school": school})

    pass


@login_required
def new_reply_to_task_view(request, pk):  # new reply / post to task

    try:
        if request.user.is_parent:
            school = request.user.parent.school
        else:
            school = request.user.teacher.school
    except ObjectDoesNotExist:
        school = None  # TODO: Admin should see tasks for all schools

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
    return render(request, 'new_reply_to_task.html', {"task": task, "form": form,
                                                      "school": school})
    pass


@login_required
def new_claim_to_task_view(request, pk):  # new reply / post to task

    task = get_object_or_404(Task, pk=pk)
    # user = User.objects.first()  # TODO: get the currently logged in user
    claim_status = get_object_or_404(Status, status=Status.PENDING_APPROVAL)  # OPEN

    try:
        if request.user.is_parent:
            school = request.user.parent.school
        else:
            school = request.user.teacher.school
    except ObjectDoesNotExist:
        school = None  # TODO: Admin should see tasks for all schools

    if request.method == 'POST':
        form = NewClaimForm(request.POST)
        if form.is_valid():

            Task.objects.filter(pk=pk).update(status=Status.IN_PROGRESS)  # i.e. update task status to in progress
            # TODO: Loses 404 check, look for a better way for task status update

            claim = form.save(commit=False)
            claim.created_by = request.user
            # post.save() # TODO: Enable after migrating , added null=True for FKs

            claim = Claim.objects.create(
                message=form.cleaned_data.get('message'),
                task=task,
                status=claim_status,
                created_by=request.user
                # TODO: Update task.status to IN PROGRESS
            )
            return redirect('task_replies', pk=task.pk)
    else:
        form = NewClaimForm()
    return render(request, 'new_claim_to_task.html', {"task": task, "form": form,
                                                      "school": school})
    pass


# @login_required
# def reply_to_post_view(request, pk, post_id):  # new reply to post
#     task = get_object_or_404(Task, pk=pk)
#     post = Task.posts.get(id=post_id)
#     data = {"task": task, "post": post}
#
#     return render(request, 'reply_to_post.html', data)
#     pass


# @login_required  # decorator throws a object has no attribute 'as_view' error
@method_decorator(login_required, name='dispatch')
class TaskUpdateView(UpdateView):

    model = Task
    fields = ('name', 'success_criteria', 'expires_on', 'reward')
    # TODO: Edit / Update from fields need to look better

    template_name = 'edit_task.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'task'

    # Fix for other users editing anyone's tasks problem
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

    # fixed: for other users deleting any posts / replies problem
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)
        pass

    def form_valid(self, form):
        post = form.delete()


# @login_required  # decorator throws a object has no attribute 'as_view' error
@method_decorator(login_required, name='dispatch')
class ClaimUpdateView(UpdateView):

    model = Claim
    fields = ('message', )
    template_name = 'edit_claim.html'
    pk_url_kwarg = 'claim_pk'
    context_object_name = 'claim'

    # TODO: fix for other users editing any posts / replies problem
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)
        pass

    def form_valid(self, form):
        claim = form.save(commit=False)
        claim.updated_by = self.request.user
        claim.updated_at = timezone.now()
        claim.save()
        return redirect('task_replies', pk=claim.task.pk)  # , post_pk=post.pk)


@method_decorator(login_required, name='dispatch')
class ClaimDeleteView(DeleteView):

    model = Claim
    template_name = 'delete_claim.html'
    pk_url_kwarg = 'claim_pk'
    context_object_name = 'claim'

    def get_success_url(self):
        task = self.object.task
        return reverse_lazy('task_replies', kwargs={'pk': task.pk})

    # fixed: for other users deleting any posts / replies problem
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)
        pass

    def form_valid(self, form):
        # TODO: Reset task status to OPEN
        post = form.delete()
        Task.object.filter(pk=post.task.pk).update(status=Status.OPEN)


@login_required
def claim_approve_view(request, pk, claim_pk):  # new reply / post to task

    task = get_object_or_404(Task, pk=pk)
    # user = User.objects.first()  # TODO: get the currently logged in user

    try:
        if request.user.is_parent:
            school = request.user.parent.school
        else:
            school = request.user.teacher.school
    except ObjectDoesNotExist:
        school = None  # TODO: Admin should see tasks for all schools

    if request.method == 'POST':
        form = ClaimApprovalForm(request.POST)

        if form.is_valid():

            Task.objects.filter(pk=pk).update(status=Status.PENDING_PAYMENT)  # i.e. update task status to in progress
            # TODO: Loses 404 check, look for a better way for task status update

            claim = form.save(commit=False)
            claim.created_by = request.user
            claim.updated_by = request.user
            claim.updated_at = timezone.now()

            Claim.objects.filter(task=task).update(status=Status.APPROVED)  # i.e. update task status to in progress

            # claim.save()
            return redirect('task_replies', pk=pk)
    else:
        claim = Claim.objects.get(pk=claim_pk)
        form = ClaimApprovalForm()
    return render(request, 'approve_claim.html', {"claim": claim, "form": form, "school": school})
    pass