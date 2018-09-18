from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm, Textarea, CharField, MultiValueField, DateTimeInput, ChoiceField
from .models import Task, Post, Claim

# ref: https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#overriding-the-default-fields


class NewTaskForm(ModelForm):

    class Meta:
        model = Task
        fields = ('name', 'success_criteria', 'reward', 'expires_on', )
        # 'expires_on' is inside the new_task.html

        widgets = {
            'success_criteria': Textarea(attrs={'cols': 80, 'rows': 4}),
            'expires_on': DateTimeInput(attrs={'class': 'datetimepicker'})
            # TODO: Add a datetime picker in the Create Task Form
        }
        labels = {
            'name': _('Task Name'),
        }
        help_texts = {
            'name': _('Enter a short task name here (up to 50 characters)'),
            'success_criteria': _('List criteria that define success for this task. Limit 320 characters'),
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
            'message': _('Enter a short reply here.')
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
