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

from .models import Task, Post, Reward, Status, Claim, Parent, Teacher, User, School, Payment, Contact
from .forms import (NewTaskForm, NewReplyForm, NewClaimForm, ClaimApprovalForm, NewSchoolForm, NewPaymentForm,
                    TaskUpdateForm, ClaimUpdateForm, ContactUsForm)


from django.core.exceptions import ObjectDoesNotExist

from django.contrib import messages
from .filters import TaskFilter
import json

from tumidpandora_school_rewards import settings


from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
import datetime

from_email = "noreply@task-a-thon.com"

def home_view(request):
    return render(request, 'home.html')


def aboutus_view(request):
    return render(request, 'about_us.html')


def contactus_view(request):

    today = datetime.datetime.now()

    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        # reward = Reward.objects.get(id=request.POST['reward'])  # Get reward from select field
        if form.is_valid():
            contact = form.save(commit=False)

            # if request.user:
            #     em = request.user.email
            # else:

            ts = today  # Set new task status to Open
            message = form.cleaned_data.get('message')

            # form.save()

            req_email = form.cleaned_data.get('req_email')

            contact = Contact.objects.create(
                req_email=req_email,
                # ts=ts,
                message=message
            )

            # EMAIL ALERT START
            subject = "Thank you for contacting Task-a-Thon"
            preheader = "We have received your support request."
            to_email = list()
            to_email.append(req_email)  # send to requestor and bcc personal email
            bcc_email = 'mohapsat@gmail.com'  # replace with a dedicated mailbox for task-a-thon
            ctx = {"req_email": req_email,
                   # "school": school,
                   "message": message,
                   "contact_time": ts,
                   "preheader": preheader  # for email pre-header var defined in email_header.html
                   }

            print("ctx = %s" % ctx)

            message = get_template('emails/new_contact_email.html').render(ctx)
            msg = EmailMessage(subject, message, to=to_email, from_email=from_email, bcc=[bcc_email])
            msg.content_subtype = 'html'
            msg.send()
            # EMAIL ALERT END

            messages.success(request, 'THANK YOU!! We have received your request and will get back'
                                      'to you at the earliest.')

            return redirect('contact_us')
        else:
            messages.error(request, 'OOPS! Please fix the errors and resubmit your request.', extra_tags='alert-warning')

    else:
        form = ContactUsForm()
    return render(request, 'contact_us.html', {"form": form})

    pass


def privacy_view(request):
    return render(request, 'privacy.html')


def pricing_view(request):
    return render(request, 'pricing.html', {"email_support": settings.EMAIL_SUPPORT,
                                            "premium_cost": settings.PREMIUM_MEMBERSHIP_COST})


# FnBasedVw implementation - refer to ClsBsdVw below
@login_required
def tasks_view(request):

    today = datetime.datetime.now()  # to filter tasks by year / month etc
    # ref: https://stackoverflow.com/questions/28101480/how-can-i-query-for-objects-in-current-year-current-month-in-django

    # TODO: Determine if view is the best place to filter tasks or pass all tasks and schools to template
    try:
        if request.user.is_parent:
            school = request.user.parent.school
        # elif request.user.is_teacher and request.school.is_active:
        else:
            school = request.user.teacher.school
    except ObjectDoesNotExist:
        school = None
        # TODO: Admin should see tasks for all schools

    # TODO: Filter tasks by school - DONE.
    # TODO: Hide closed tasks from previous year

    tasks = Task.objects.filter(school=school).order_by('-last_updated')  # .exclude(status__in=[7,6])

    task_filter = TaskFilter(request.GET, queryset=tasks)

    page = request.GET.get('page', 1)

    page_size = 5  # shows #tasks in one page

    paginator = Paginator(task_filter.qs, page_size)
    # paginator = Paginator(tasks, 1)
    # changed from tasks to task_filter.qs

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

    chart_height = 175  # applies to all charts

    # REF: https://simpleisbetterthancomplex.com/tutorial/2016/12/06/how-to-create-group-by-queries.html
    # status 7 is 'PAID'

    # TODO: Filter tasks by current year

    chart_left_data = Task.objects.filter(school=school).filter(last_updated__year=today.year).filter(status=7).values('reward__name')\
        .annotate(Sum('reward__amount'))
    # paid_rewards_total = chart_left_data[0]['reward__amount__sum']
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
        'chart': {'type': 'pie', 'height': chart_height},  # column, pie, area, line
        'title': {'text': '$ Rewards Paid YTD'},
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

    chart_middle_data = Task.objects.filter(school=school).filter(last_updated__year=today.year).values('status')\
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
        elif entry['status'] == 7:
            entry['status'] = 'Paid'

        chart_middle_categories.append(entry['status'])
        chart_middle_counts_series.append({'name': entry['status'], 'y': entry['id__count']})

    # print("chart_middle_categories = %s" % chart_middle_categories)

    chart_middle_counts_series = {
        'name': 'Tasks',
        'colorByPoint': 'true',
        'data': chart_middle_counts_series
    }

    chart_middle = {
        'chart': {'type': 'bar', 'height': chart_height},  # column, pie, area, line
        'title': {'text': '# Task Statuses YTD'},
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
    chart_right_data = Task.objects.filter(school=school).filter(last_updated__year=today.year). \
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
        'chart': {'type': 'column', 'height': chart_height},  # column, pie, area, line
        'title': {'text': '# Reward Claims YTD'},
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

    return render(request, 'tasks.html', {'tasks': tasks, 'school': school, 'task_filter': task_filter,
                                          'chart_left': dump_left, #"paid_rewards_total": paid_rewards_total,
                                          'chart_middle': dump_middle,
                                          'chart_right': dump_right
                                          })
    # pass


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

    paginator = Paginator(queryset, 10)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # messages.info(request, 'THIS SCREEN HAS MORE DETAILS ON THE ASSIGNMENT.')
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
                reward=reward,
                grade=form.cleaned_data.get('grade')
            )
            messages.success(request, 'THANK YOU! YOUR TASK WAS CREATED SUCCESSFULLY!')

            # EMAIL ALERT START
            subject = "New Task Created."
            preheader = "Thank you for creating a new task."
            em = request.user.email     # task owner
            to_email = list()
            to_email.append(em)
            bcc_email = "support@task-a-thon.com"
            ctx = {"task_name": form.cleaned_data.get('name'),
                   # "school": school,
                   "success_criteria": form.cleaned_data.get('success_criteria'),
                   "reward": reward,
                   "preheader": preheader  # for email pre-header var defined in email_header.html
                   }

            # print("ctx = %s" % ctx)

            message = get_template('emails/new_task_email.html').render(ctx)
            msg = EmailMessage(subject, message, to=to_email, from_email=from_email)
            msg.content_subtype = 'html'
            msg.send()
            # EMAIL ALERT END

            return redirect('tasks')
        else:
            messages.error(request, 'Please fix the errors and retry.', extra_tags='alert-warning')

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
            messages.success(request, 'AWESOME! YOUR REPLY WAS CREATED SUCCESSFULLY!')
            return redirect('task_replies', pk=task.pk)
        else:
            messages.warning(request, 'Apologies, please fix the errors and retry.')
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
            messages.success(request, 'THANK YOU! YOUR REWARD CLAIM # %s WAS CREATED SUCCESSFULLY!' % claim.id)


            # EMAIL ALERT START
            subject = "YAY! Your task is complete. Time to Approve!"
            preheader = "Thank you for completing a task."
            em = request.user.email     # task owner
            to_email = [request.user.email, task.starter.email]  # to task and claim owners
            # to_email = list()
            # to_email.append(em)
            bcc_email = "support@task-a-thon.com"
            ctx = {"task_name": task.name,
                   # 'task_starter_first_name': task.starter.first_name,
                   # 'task_starter_last_name': task.starter.last_name,
                   'claim_message': claim.message,
                   'created_on': claim.created_at,
                   'claim_status': claim.status,
                   "reward": task.reward,
                   "preheader": preheader  # for email pre-header var defined in email_header.html
                   }

            # print("ctx = %s" % ctx)

            message = get_template('emails/new_claim_email.html').render(ctx)
            msg = EmailMessage(subject, message, to=to_email, from_email=from_email)
            msg.content_subtype = 'html'
            msg.send()
            # EMAIL ALERT END

            return redirect('task_replies', pk=task.pk)
        else:
            messages.info(request, 'OOPS! Please fix errors below and retry.')
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

    # TODO: Edit / Update from fields need to look better
    # Ref: https://stackoverflow.com/questions/42046636/change-widget-from-select-to-check-box-in-generic-class-based-view
    # fields = ('name', 'grade', 'success_criteria', 'expires_on', 'reward')
    form_class = TaskUpdateForm

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
        messages.warning(self.request, "Task updated successfully!")
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

    def get_form(self):
        form = super(PostUpdateView, self).get_form()
        return form

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

    # TODO: Edit / Update from fields need to look better
    # Ref: https://stackoverflow.com/questions/42046636/change-widget-from-select-to-check-box-in-generic-class-based-view
    # fields = ('message', )
    form_class = ClaimUpdateForm

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
        messages.warning(self.request, "Reward Claim updated successfully!")
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
        Task.objects.filter(pk=self.task.pk).update(status=Status.OPEN)
        messages.warning(self.request, "Reward Claim deleted successfully!")
        claim = form.delete()


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
            messages.success(request, 'COOL! THANK YOU FOR APPROVING THE CLAIM!')
            return redirect('task_replies', pk=pk)
    else:
        claim = Claim.objects.get(pk=claim_pk)
        form = ClaimApprovalForm()
    return render(request, 'approve_claim.html', {"claim": claim, "form": form,
                                                  "school": school})
    pass


def new_payment_to_task_view(request, pk):

    task = get_object_or_404(Task, pk=pk)

    try:
        if request.user.is_parent:
            school = request.user.parent.school
        else:
            school = request.user.teacher.school
    except ObjectDoesNotExist:
        school = None

    if request.method == 'POST':
        form = NewPaymentForm(request.POST)
        if form.is_valid():
            Task.objects.filter(pk=pk).update(status=Status.PAID)  # i.e. update payment status to PAID_PENDING_CONFIRMATION
            payment = form.save(commit=False)
            payment.created_by = request.user
            payment.save()
            messages.success(request, 'THANKS! YOUR PAYMENT WAS RECORDED SUCCESSFULLY!.')
            return redirect('task_replies', pk=pk)
    else:
        # payment = Payment.objects.get(pk=payment_pk)
        form = NewPaymentForm()
    return render(request, 'new_payment_to_task.html', {"form": form, "school": school,
                                                        "task": task})
    pass


def new_school_view(request):  # create new school

    if request.method == 'POST':
        form = NewSchoolForm(request.POST)

        if form.is_valid():
            # school = form.save(commit=False)
            # school.save()  # TODO: Enable after migrating , added null=True for FKs

            name = form.cleaned_data.get('name')
            street_address = form.cleaned_data.get('street_address')
            city = form.cleaned_data.get('city')
            state = form.cleaned_data.get('state')
            zip_code = form.cleaned_data.get('zip_code')
            paypal_account = form.cleaned_data.get('paypal_account')
            requested_by_email = form.cleaned_data.get('requested_by_email')

            school = School.objects.create(
                name=name,
                street_address=street_address,
                city=city,
                state=state,
                zip_code=zip_code,
                paypal_account=paypal_account,
                requested_by_email=requested_by_email
            )
            messages.info(request, 'SUCCESS! NEW SCHOOL REQUEST SUBMITTED.')

        # EMAIL ALERT START
            subject = "New School Request Submitted."
            preheader = "Thank you, we have received your request"
            em = requested_by_email
            to_email = list()
            to_email.append(em)
            bcc_email = "support@task-a-thon.com"
            ctx = {"name": name,
                   "requested_by_email": requested_by_email,
                   "street_address": street_address,
                   "city": city,
                   "state": state,
                   "zip_code": zip_code,
                   "paypal_account": paypal_account,
                   "preheader": preheader  # for email preheader var defined in email_header.html
                   }

            # print("ctx = %s" % ctx)

            message = get_template('emails/new_school_request.html').render(ctx)
            msg = EmailMessage(subject, message, to=to_email, from_email=from_email, bcc=[bcc_email])
            msg.content_subtype = 'html'
            msg.send()
        # EMAIL ALERT END

            return redirect('new_school')
        # else:
        #     messages.warning(request, 'Please correct the errors below')
    else:
        form = NewSchoolForm()
    return render(request, 'new_school.html', {"form": form})

    # TODO: Show success message, after creating school. Don't switch to login quickly!!

    pass

# REF: https://docs.djangoproject.com/en/2.1/ref/views/#error-views


def error_400_view(request, exception):  # Bad Request
    return render(request, '404.html')


def error_403_view(request, exception):  # HTTP Forbidden
    return render(request, '404.html')


def error_404_view(request, exception):  # Page not found
    return render(request, '404.html')


def error_500_view(request, exception):   # Server Error
    return render(request, '404.html')



