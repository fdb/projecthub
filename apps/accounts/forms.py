import re

from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import SafeString
from django.conf import settings

domain_expression = re.compile('^.*@(.*)$')

class UserCreateForm(forms.Form):
    username = forms.CharField(min_length=5, max_length=20)
    password = forms.CharField(min_length=5, max_length=20, widget=forms.PasswordInput)
    password_again = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()
    captcha = forms.CharField()
    
    def __init__(self, word, data=None):
        super(UserCreateForm, self).__init__(data)
        self.word = word

    def clean_username(self):
        if self.cleaned_data.get('username'):
            try:
                User.objects.get(username__exact=self.cleaned_data['username'])
                raise forms.ValidationError(u'Username "%s" already exists.' % self.cleaned_data['username'])
            except User.DoesNotExist:
                pass
        return self.cleaned_data['username']

    def clean(self):
        if self.cleaned_data.get('password') and self.cleaned_data.get('password_again') and self.cleaned_data['password'] != self.cleaned_data['password_again']:
            raise forms.ValidationError(u'Please make sure your passwords match.')
        return self.cleaned_data

    def clean_email(self):
        if self.cleaned_data.get('email'):
            try:
                User.objects.get(email__exact=self.cleaned_data['email'])
                raise forms.ValidationError(u'Email "%s" already exists. Go to %saccounts/forgot/ to reset your password.' % (self.cleaned_data['email'], settings.SITE_URL))
            except User.DoesNotExist:
                pass
            match = re.match(domain_expression, self.cleaned_data['email'])
            if match is None:
                raise forms.ValidationError(u'Email is not from a valid domain.')
            if match.groups()[0] in settings.BOGUS_EMAIL_DOMAINS:
                raise forms.ValidationError(u'Email is from a known bogus domain.')
        return self.cleaned_data['email']
        
    def clean_captcha(self):
        if self.cleaned_data.get('captcha') is None:
            raise forms.ValidationError(u'This field cannot be empty.')
        if self.cleaned_data['captcha'] != self.word:
            raise forms.ValidationError(u'Doesn\'t match captcha.')
        return self.cleaned_data['captcha']


class UserEditForm(forms.Form):
    
    old_password = forms.CharField(required=False, widget=forms.PasswordInput)
    password = forms.CharField(required=False, widget=forms.PasswordInput)
    password_again = forms.CharField(required=False, widget=forms.PasswordInput)
    email = forms.EmailField()

    def __init__(self, user, data=None):
        super(UserEditForm, self).__init__(data)
        self.user = user

    def clean(self):
        data = self.cleaned_data
        if data.get('password') and data.get('password_again'):
            if len(data['password']) == 0:
                return data
            if data.get('old_password') is None or len(data['old_password']) == 0:
                raise forms.ValidationError(u'Provide old pass')
            if not self.user.check_password(data['old_password']):
                raise forms.ValidationError(u'Old pw wrong')
            if len(data['password']) < 5:
                raise forms.ValidationError(u'Too short')
            if len(data['password']) > 20:
                raise forms.ValidationError(u'Too long')
            if data['password'] != data['password_again']:
                raise forms.ValidationError(u'Don\'t match')
        return data
