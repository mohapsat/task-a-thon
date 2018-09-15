from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import SignUpForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView


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
    fields = ('first_name', 'last_name', 'email', 'username',)
    template_name = 'my_account.html'
    success_url = reverse_lazy('tasks')

    def get_object(self):
        return self.request.user
