from django.db.models import Count, Q, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import SignUpForm, ParentSignUpForm, TeacherSignUpForm

from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView, DeleteView, ListView

from rewards.models import (User, School, Parent, Teacher, Reward, Task, Claim)

from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

from django.http import HttpResponse


# Create your views here.
def signup_view(request):

        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect('tasks')
        else:
            form = SignUpForm()
        return render(request, 'signup.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email', 'username', )
    template_name = 'my_account.html'
    success_url = reverse_lazy('tasks')

    def get_object(self):
        return self.request.user
    # TODO: Pass school info to user update view


def parent_signup_view(request):

    if request.method == 'POST':
        form = ParentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tasks')
    else:
        form = ParentSignUpForm()
    return render(request, 'signup.html', {'form': form})

    pass


def teacher_signup_view(request):

    if request.method == 'POST':
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tasks')
    else:
        form = TeacherSignUpForm()
    return render(request, 'signup.html', {'form': form})

    pass


@login_required
def my_school_view(request):

    try:
        if request.user.is_parent:
            school = request.user.parent.school
        else:
            school = request.user.teacher.school
    except ObjectDoesNotExist:
        school = None  # TODO: Admin should see tasks for all schools

    teachers = Teacher.objects.filter(school=school).filter(is_school_admin=False).order_by('user__last_login')
    # teachers = Teacher.objects.filter(school=school).order_by('user__last_login')
    # print("teachers = %s" % teachers)

    # TODO: Add parents to admin view (if required)
    parents = Parent.objects.filter(school=school).order_by('user__last_login')
    # print("parents = %s" % parents)

    page = request.GET.get('page', 1)

    paginator = Paginator(teachers, 10)

    try:
        teachers = paginator.page(page)
    except PageNotAnInteger:
        teachers = paginator.page(1)
    except EmptyPage:
        teachers = paginator.page(paginator.num_pages)

    return render(request, 'my_school.html', {"school": school, "teachers": teachers,
                                              "parents": parents
                                              # TODO: Add parents to admin view (if required)
                                              })
    pass


# @login_required
# def activate_user_view(request, pk):
#     return HttpResponse("Activate " + pk)
#     pass


@method_decorator(login_required, name='dispatch')
class ActivateUserView(UpdateView):

    model = User
    fields = ('id', )  # just a placeholder, needed to have at least one field.
    template_name = 'activate_user.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'user'


    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.filter(created_by=self.request.user)
    #     pass

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True
        # user.updated_by = self.request.user
        # claim.updated_at = timezone.now()
        user.save()
        return redirect('my_school')


# @login_required
# def deactivate_user_view(request, pk):
#     return HttpResponse("deactivate " + pk)
#     pass

@method_decorator(login_required, name='dispatch')
class DeactivateUserView(UpdateView):

    model = User
    fields = ('id', )  # just a placeholder, needed to have at least one field.
    template_name = 'deactivate_user.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'user'


    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.filter(created_by=self.request.user)
    #     pass

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        # user.updated_by = self.request.user
        # claim.updated_at = timezone.now()
        user.save()
        return redirect('my_school')

# @login_required
# def remove_user_view(request, pk):
#     # return HttpResponse("Remove " + pk)
#     return render(request, 'remove_user.html', pk)
#     pass


@method_decorator(login_required, name='dispatch')
class RemoveUserView(DeleteView):

    model = User
    template_name = 'remove_user.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'user'

    def get_success_url(self):
        # task = get_object_or_404(Task, pk=self.pk)
        # return reverse_lazy('task_replies', kwargs={'pk': task.pk})
        return reverse_lazy('my_school')

    # fix for other users deleting any tasks problem
    # def get_queryset(self):
        # queryset = super().get_queryset()
        # return self.request.user
        # pass

    def form_valid(self, form):
        user = form.delete()

