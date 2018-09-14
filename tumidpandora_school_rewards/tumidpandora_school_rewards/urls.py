"""tumidpandora_school_rewards URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from accounts import views as account_views
from rewards import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', account_views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html',
        email_template_name='password_reset_email.html',
        subject_template_name='password_reset_subject.txt'
    ),
         name='password_reset'),

    path('reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'),
         name='password_reset_complete'),


    path('settings/password/', auth_views.PasswordChangeView.as_view(
        template_name='password_change.html'),
         name='password_change'),

    path('settings/password/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='password_change_done.html'),
         name='password_change_done'),

    path('tasks/', views.tasks_view, name='tasks'),
    # path('tasks/', views.TaskListView.as_view, name='tasks'),
    path('tasks/new/', views.new_task_view, name='new_task'),
    path('tasks/<pk>/', views.task_replies_view, name='task_replies'),
    path('tasks/<pk>/reply/', views.new_reply_to_task_view, name='new_reply_to_task'),
    path('tasks/<pk>/edit/', views.TaskUpdateView.as_view(), name='edit_task'),
    path('tasks/<pk>/delete/', views.TaskDeleteView.as_view(), name='delete_task'),
    path('tasks/<pk>/reply/<post_pk>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('tasks/<pk>/reply/<post_pk>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('admin/', admin.site.urls),
]
