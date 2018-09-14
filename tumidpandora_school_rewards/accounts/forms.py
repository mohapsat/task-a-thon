from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# UserCreationForm does not provide an email field. But we can extend it.
class SignUpForm(UserCreationForm):

    SALUTATION_CHOICES = (
        ('1', 'Mr'),
        ('2', 'Ms'),
    )

    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    # is_parent = forms.CheckboxInput(check_test=False)
    salutation = forms.ChoiceField(choices=SALUTATION_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email', 'salutation', 'password1', 'password2')
