from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm, Textarea, CharField, MultiValueField, DateTimeInput, ChoiceField, TextInput, DateTimeField, MultipleChoiceField
from .models import Task, Post, Claim, School, Payment

# ref: https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#overriding-the-default-fields


class NewTaskForm(ModelForm):

    grade = MultipleChoiceField(choices=Task.GRADE_CHOICES, required=False, initial=1,
                                label='Assign to Grade(s)'
                                )
    # FOR styling is handled in template:
    # REF: https://stackoverflow.com/questions/22592276/django-how-to-style-a-checkboxselectmultiple-in-a-form

    # TODO: Grade needs to be a multivalueselect dropdown

    class Meta:
        model = Task
        fields = ('name', 'grade', 'success_criteria', 'reward', 'expires_on')
        # TODO :'grade' is inside the new_task.html. FYI

        widgets = {
            'expires_on': DateTimeInput(attrs={'class': 'datepicker'}),
            'success_criteria': Textarea(attrs={'class': 'form-control form-control-alternative',
                                                'cols': 40, 'rows': 4}),

            # TODO: Add a datetime picker in the Create Task Form
        }
        labels = {
            'name': _('Task Name'),

        }
        help_texts = {
            'name': _('Enter a short task name here (up to 50 characters)'),
            'success_criteria': _('List criteria that define success for this task. Limit 200 characters'),
            'expires_on': _('Defaulted to +30 Days from task creation date. Please update if required.')
        }
        error_messages = {
            'name': {
                'max_length': _("This task's name is too long."),
            },
        }


class NewReplyForm(ModelForm):  # Post

    class Meta:
        model = Post
        fields = ['message']
        widgets = {
            'message': Textarea(attrs={'cols': 80, 'rows': 2}),
        }
        help_texts = {
            'message': _('Please enter a short reply here.')
        }
        localize = '_all_'


class NewClaimForm(ModelForm):  # Post

    class Meta:
        model = Claim
        fields = ['message']
        widgets = {
            'message': Textarea(attrs={'cols': 80, 'rows': 2}),
        }
        help_texts = {
            'message': _('Enter a short description to support your claim here.')
        }
        localize = '_all_'


class NewSchoolForm(ModelForm):  # School

    class Meta:
        model = School
        fields = ('name', 'paypal_account', 'street_address', 'city', 'state', 'zip_code', )
        # 'expires_on' is inside the new_task.html

        widgets = {
            'paypal_account': TextInput(attrs={'placeholder': 'PayPal.Me/YourSchool'}),
            # 'name': TextInput(attrs={'placeholder': 'Little Angles Elementary'}),
        }
        labels = {
            'name': _('School Name'),
        }
        help_texts = {
            'name': _("Enter your school's name (e.g. Little Angels Elementary)"),
            'paypal_account': _("Your school will receive payments into their Paypal account directly."
                                " Please create one here: <a target=\"_blank\" href=\"https://www.paypal.com/us/webapps/mpp/education\">"
                                "School Payment Solutions with PayPal</a>"),
        }
        error_messages = {
            'name': {
                'max_length': _("Please limit school name to 128 characters."),
            },
        }


class ClaimApprovalForm(ModelForm):

    class Meta:
        model = Claim
        fields = []  # can't create a ModelForm without the fields property, so add a blank one


class NewPaymentForm(ModelForm):

    class Meta:
        model = Payment
        fields = []  # can't create a ModelForm without the fields property, so add a blank one


class TaskUpdateForm(ModelForm):

    grade = MultipleChoiceField(choices=Task.GRADE_CHOICES,
                                initial='1',
                                label='Assign to Grade(s)')

    class Meta:
        model = Task
        fields = ['name', 'grade', 'success_criteria', 'expires_on', 'reward']
        widgets = {
            'expires_on': DateTimeInput(attrs={'class': 'datepicker'}),
            'success_criteria': Textarea(attrs={'class': 'form-control form-control-alternative',
                                                'cols': 40, 'rows': 4})
            # TODO: Add a datetime picker in the Create Task Form
        }
        labels = {
            'name': _('Task Name'),
        }
        help_texts = {
            'name': _('Enter a short task name here (up to 125 characters)'),
            'success_criteria': _('List criteria that define success for this task. Limit 200 characters'),
            'expires_on': _('Defaulted to +30 Days from task creation date. Please update if required.')
        }
        error_messages = {
            'name': {
                'max_length': _("This task's name is too long."),
            },
        }


class ClaimUpdateForm(ModelForm):

    class Meta:
        model = Claim
        fields = ['message', ]

        widgets = {
            'message': Textarea(attrs={'cols': 80, 'rows': 4}),
        }
        help_texts = {
            'message': _('Enter a short description to support your claim here.')
        }
        labels = {
            'message': _('Message to support your claim'),
        }


