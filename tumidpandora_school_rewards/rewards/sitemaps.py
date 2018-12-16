from django.contrib.sitemaps import Sitemap
from rewards.models import Task, Post, Claim, School #, Payment
from django.urls import reverse


class TaskSitemap(Sitemap):

    protocol = "https"

    def items(self):
        return Task.objects.all()


class PostSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return Post.objects.all()


class ClaimSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return Claim.objects.all()


class SchoolSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return School.objects.all()


# class PaymentSitemap(Sitemap):
#     def items(self):
#         return Payment.objects.all()  # 'NoneType' object has no attribute 'id' since no payment exists

class StaticViewSitemap(Sitemap):

    # changefreq = 'always'

    protocol = "https"

    def items(self):
        return ['home', 'about_us', 'pricing', 'privacy',
                'parent_signup', 'teacher_signup', 'my_account',
                'upgrade_account', 'my_school', 'login',
                'logout', 'password_reset', 'password_change', 'new_school',
                'pricing']

    def location(self, obj):
        return reverse(obj)

