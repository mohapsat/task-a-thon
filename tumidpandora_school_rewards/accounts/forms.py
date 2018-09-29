from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
# from django.contrib.auth.models import User

from rewards.models import (School, Task, Reward,
                            Parent, Teacher, User)


# UserCreationForm does not provide an email field. But we can extend it.
class SignUpForm(UserCreationForm):

    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    # is_parent = forms.CheckboxInput(check_test=False)
    # salutation = forms.ChoiceField(choices=SALUTATION_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ParentSignUpForm(UserCreationForm):
    # SALUTATION_CHOICES = (
    #     ('1', 'Mr'),
    #     ('2', 'Ms'),
    # )

    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    # salutation = forms.ChoiceField(choices=SALUTATION_CHOICES)
    school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        widget=forms.Select(),
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('school', 'first_name', 'last_name', 'username', 'email', 'password1', 'password2',)
        # TODO: set "---------" by default) with the empty_label attribute to "Select a School"
        help_texts = {
            'school': _("Can't find your school? Please contact mailto:support@schoolrewards.com")
        }


    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_parent = True
        user.save()

        parent = Parent.objects.create(user=user, school=self.cleaned_data.get('school'))

        return user


class TeacherSignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())

    school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        widget=forms.Select(),
        required=True,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('school', 'first_name', 'last_name', 'username', 'email', 'password1', 'password2',)

    @transaction.atomic  # so all transaction happen together
    def save(self):
        user = super().save(commit=False)
        user.is_teacher = True
        user.save()

        teacher = Teacher.objects.create(user=user, school=self.cleaned_data.get('school'))

        # teacher = Teacher.objects.create(user=user)
        # teacher.t_schools.add(*self.cleaned_data.get('school'))
        return user