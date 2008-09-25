from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name':'accounts/login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page':'/'}),
    (r'^create/$', 'gravital_website.apps.accounts.views.create'),
    (r'^welcome/$', 'gravital_website.apps.accounts.views.welcome'),
    (r'^check-your-email/$', 'gravital_website.apps.accounts.views.verify'),
    (r'^forgot/$', 'django.contrib.auth.views.password_reset', {'template_name':'accounts/password_reset_form.html', 'email_template_name':'accounts/password_reset_email.html'}),
    (r'^forgot/done/$', 'django.contrib.auth.views.password_reset_done', {'template_name':'accounts/password_reset_done.html'}),
    (r'^edit/$', 'gravital_website.apps.accounts.views.edit'),
    (r'^captcha/$', 'gravital_website.apps.accounts.views.captcha'),
)
