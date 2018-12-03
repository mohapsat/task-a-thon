from django.db.models import Count, Q, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import SignUpForm, ParentSignUpForm, TeacherSignUpForm, UpgradeAccountForm

from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView, DeleteView, ListView

from rewards.models import (User, School, Parent, Teacher, Reward, Task, Claim, UpgradeCharge)

from tumidpandora_school_rewards import settings

from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from django.contrib import messages
from django.http import HttpResponse

import stripe
import datetime


from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.dispatch import receiver  # signal for tracking log out
from django.contrib import messages

from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage

from_email = "noreply@task-a-thon.com"
stripe.api_key = settings.STRIPE_SECRET_KEY


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
    fields = ('first_name', 'last_name', 'email', 'username')
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
            messages.warning(request, "WELCOME! NEW PARENT ACCOUNT CREATED!")
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
            messages.warning(request, "WELCOME! NEW TEACHER ACCOUNT CREATED!")
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

    # teachers = Teacher.objects.filter(school=school).filter(is_school_admin=False).order_by('user__last_login')
    teachers = Teacher.objects.filter(school=school).order_by('user__last_login')
    # TODO: Don't filter admin users from the list

    paginator = Paginator(teachers, 4)  # #teacher records seen at one page
    page = request.GET.get('t_page')

    try:
        teachers = paginator.page(page)
    except PageNotAnInteger:
        teachers = paginator.page(1)
    except EmptyPage:
        teachers = paginator.page(paginator.num_pages)

    # print("teachers = %s" % teachers)

    # TODO: Add parents to admin view (if required)
    parents = Parent.objects.filter(school=school).order_by('user__last_login')
    # print("parents = %s" % parents)

    paginator = Paginator(parents, 4)  # #parent records seen at one page
    page = request.GET.get('p_page')

    try:
        parents = paginator.page(page)
    except PageNotAnInteger:
        parents = paginator.page(1)
    except EmptyPage:
        parents = paginator.page(paginator.num_pages)

    print("parents = %s" % parents)

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
        # messages.success(user, "Success! user activated successfully!")
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


# TODO: Create a job to expire accounts daily
@login_required
def upgrade_account_view(request):

    try:
        if request.user.is_parent:
            school = request.user.parent.school
        else:
            school = request.user.teacher.school
    except ObjectDoesNotExist:
        school = None  # TODO: Admin should see tasks for all schools

    # teachers_count = Teacher.objects.filter(school=school).Count('id')
    # parents_count = Parent.objects.filter(school=school).Count('id')
    # tasks_count = Task.objects.filter(school=school).Count('id')
    # claims_count =
    # rewards_total =

    teachers_count = 10
    parents_count = 5
    tasks_count = 45
    claims_count = 23
    rewards_total = 600

    stripe_premium_charge = settings.PREMIUM_MEMBERSHIP_COST.replace(".", "")  # replace period for stripe charge

    return render(request, 'upgrade_account.html', {"stripe_key": settings.STRIPE_PUBLISHABLE_KEY,
                                                    "stripe_premium_charge": stripe_premium_charge,  # no need to change
                                                    "premium_cost": settings.PREMIUM_MEMBERSHIP_COST,
                                                    "email_support": settings.EMAIL_SUPPORT,
                                                    "school": school,
                                                    "teachers_count": teachers_count,
                                                    "parents_count": parents_count,
                                                    "tasks_count": tasks_count,
                                                    "claims_count": claims_count,
                                                    "rewards_total": rewards_total})


@login_required
def upgrade_account_confirm_view(request):

# When a user submits the form (ie: pays), their bank account
# information is sent to stripe for processing.
# If the payment is accepted, stripe will issue a POST request
# to the endpoint specified in the action attribute of the form.
# The idea is to then capture that token and use it to charge the user’s card.

# We create an upgradeCharge based on this post request from stripe

    # amount = int(float(settings.PREMIUM_MEMBERSHIP_COST))
    stripe_premium_charge = settings.PREMIUM_MEMBERSHIP_COST.replace(".", "")  # replace period for stripe charge

    now = datetime.datetime.now()  # used to store charge time

    try:
        if request.user.is_parent:
            school = request.user.parent.school
        else:
            school = request.user.teacher.school
    except ObjectDoesNotExist:
        school = None  # TODO: Admin should see tasks for all schools

    if request.method == 'POST':

        form = UpgradeAccountForm(request.POST)
        if form.is_valid():

            token = request.POST.get("stripeToken")

            try:
                charge = stripe.Charge.create(
                    amount=stripe_premium_charge,
                    currency="usd",
                    source=token,
                    description="")

                if school is not None:
                    School.objects.filter(id=school.id).update(is_paid=True)  # enable premium
                # TODO: Daily job to check for premium status expiring

                # create charge
                upgrade_charge = form.save(commit=False)
                upgrade_charge.save()

                payee = request.user
                charge_id = charge.id  # from stripe charge object

                upgrade_charge = UpgradeCharge.objects.create(
                    charge_success=True,
                    school=school,
                    created_by=payee,
                    amount=299.99,  # settings.PREMIUM_MEMBERSHIP_COST
                    charge_id=charge_id,
                    created_at=now
                    )
                return render(request, 'upgrade_payment_confirm.html', {"email_support": settings.EMAIL_SUPPORT,
                                                                        "school": school,
                                                                        "charge_id": charge_id,
                                                                        "created_by": payee,
                                                                        "created_datetime": now})

            except stripe.error.CardError as ce:
                # return False, ce
                # TODO: add failure notification
                return render(request, 'upgrade_account.html', {"form": form,
                                                                "email_support": settings.EMAIL_SUPPORT,
                                                                "school": school})
    else:
        form = UpgradeAccountForm()
        return render(request, 'upgrade_account.html', {"form": form,
                                                        "email_support": settings.EMAIL_SUPPORT,
                                                        "school": school})


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
        if user:
            msg = 'WELCOME! YOU HAVE SECURELY LOGGED IN.'
        else:
            msg = 'WELCOME! YOU HAVE SECURELY LOGGED IN.'
        messages.success(request, msg)


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
        if user:
            msg = 'YOU HAVE SUCCESSFULLY LOGGED OUT'
        else:
            msg = None  # TODO: Msg shows up on login as well for some reason
        messages.success(request, msg)


user_logged_out.connect(on_user_logged_out)
