from django import forms
from .models import Task, Post, Status
import django_filters


# REF: https://simpleisbetterthancomplex.com/tutorial/2016/11/28/how-to-filter-querysets-dynamically.html
class TaskFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(lookup_expr='icontains', label='',)
    # status = django_filters.ModelMultipleChoiceFilter(queryset=Status.objects.all(),
    #     widget=forms.Select)

    # expires_on = django_filters.DateTimeFilter(lookup_expr='exact')

    class Meta:
        model = Task
        fields = ['name']
