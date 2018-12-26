from django.contrib import admin
from django.urls import path

from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap

from accounts import views as accounts_views
from rewards import views

from rewards.sitemaps import SchoolSitemap, TaskSitemap, ClaimSitemap, PostSitemap, StaticViewSitemap  # , PaymentSitemap


sitemaps = {
    'static_pages': StaticViewSitemap,

    'tasks': TaskSitemap,
    'posts': PostSitemap,
    'claims': ClaimSitemap,
    'my_schools': SchoolSitemap,
    # 'payments': PaymentSitemap,

    # 'status': StatusSitemap,
}

urlpatterns = [

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),

    path('', views.home_view, name='home'),
    path('about/', views.aboutus_view, name='about_us'),
    path('contact/', views.contactus_view, name='contact_us'),
    path('pricing/', views.pricing_view, name='pricing'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('press/', views.press_view, name='press'),
    path('signup/', accounts_views.signup_view, name='signup'),

    path('signup/parent/', accounts_views.parent_signup_view, name='parent_signup'),  # parent_signup
    path('signup/teacher/', accounts_views.teacher_signup_view, name='teacher_signup'),  # teacher_signup

    path('settings/account/', accounts_views.UserUpdateView.as_view(), name='my_account'),
    path('settings/upgrade/', accounts_views.upgrade_account_view, name='upgrade_account'),
    path('settings/upgrade/confirm', accounts_views.upgrade_account_confirm_view, name='upgrade_confirm'),

    path('settings/school/', accounts_views.my_school_view, name='my_school'),
    path('settings/school/activate/<pk>', accounts_views.ActivateUserView.as_view(), name='activate_user'),
    path('settings/school/deactivate/<pk>', accounts_views.DeactivateUserView.as_view(), name='deactivate_user'),
    path('settings/school/remove/<pk>', accounts_views.RemoveUserView.as_view(), name='remove_user'),


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

    path('schools/new/', views.new_school_view, name='new_school'),

    path('tasks/', views.tasks_view, name='tasks'),
    path('tasks/new/', views.new_task_view, name='new_task'),

    path('tasks/search/', views.tasks_view, name='search_tasks'),

    path('tasks/<pk>/', views.task_replies_view, name='task_replies'),
    path('tasks/<pk>/edit/', views.TaskUpdateView.as_view(), name='edit_task'),
    path('tasks/<pk>/delete/', views.TaskDeleteView.as_view(), name='delete_task'),

    path('tasks/<pk>/reply/', views.new_reply_to_task_view, name='new_reply_to_task'),
    path('tasks/<pk>/reply/<post_pk>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('tasks/<pk>/reply/<post_pk>/delete/', views.PostDeleteView.as_view(), name='delete_post'),

    path('tasks/<pk>/pay/', views.new_payment_to_task_view, name='new_payment_to_task'),

    path('tasks/<pk>/claim/', views.new_claim_to_task_view, name='new_claim_to_task'),
    path('tasks/<pk>/claim/<claim_pk>/approve/', views.claim_approve_view, name='approve_claim'),
    path('tasks/<pk>/claim/<claim_pk>/edit/', views.ClaimUpdateView.as_view(), name='edit_claim'),
    path('tasks/<pk>/claim/<claim_pk>/delete/', views.ClaimDeleteView.as_view(), name='delete_claim'),


    path('admin/', admin.site.urls),
]

# ERROR VIEWS
handler400 = views.error_400_view  # Bad Request
handler403 = views.error_403_view  # HTTP Forbidden
handler404 = views.error_404_view  # Page not found
handler500 = views.error_500_view  # Server Error
