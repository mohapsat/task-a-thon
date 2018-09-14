from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm, Textarea, CharField, MultiValueField
from .models import Task, Post

# ref: https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#overriding-the-default-fields


class NewTaskForm(ModelForm):

    class Meta:
        model = Task
        fields = ('name', 'success_criteria', 'reward', 'expires_on')
        # TODO: concatenate reward and amount in form display

        widgets = {
            'success_criteria': Textarea(attrs={'cols': 80, 'rows': 4}),
        }
        labels = {
            'name': _('Task Name'),
        }
        help_texts = {
            'name': _('Enter a short task name here (up to 50 characters)'),
            'success_criteria': _('List criteria that define success for this task. Limit 320 characters'),
            'expires_on':_('Defaulted to +30 Days from task creation date. Please update if required.')
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
