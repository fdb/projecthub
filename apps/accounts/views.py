from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from gravital.apps.accounts.forms import UserCreateForm, UserEditForm
from gravital.util.captcha import makekey, makeword, makeimage

def create(request):
    if request.method == 'GET':
        key = makekey()
        request.session['captcha_word'] = word = makeword(key)
        user_form = UserCreateForm(word)
    elif request.method == 'POST':
        word = request.session['captcha_word']
        user_form = UserCreateForm(word, request.POST)
        if user_form.is_valid():
            data = user_form.cleaned_data
            new_user = User.objects.create_user(data['username'], data['email'], data['password'])
            new_user.save()
            # Hack so I can use login method.
            user = authenticate(username=new_user.username, password=data['password'])
            if user is not None:
                login(request, user)
            return HttpResponseRedirect('/accounts/welcome/')
    return render_to_response('accounts/create.html', {'form':user_form}, RequestContext(request))
    
def welcome(request):
    return render_to_response('accounts/welcome.html', RequestContext(request))

def verify(request):
    return render_to_response('accounts/verify.html', RequestContext(request))
    
def edit(request):
    if request.method == 'GET':
        user_form = UserEditForm(request.user, dict(email=request.user.email))
    elif request.method == 'POST':
        user_form = UserEditForm(request.user, request.POST)
        if user_form.is_valid():
            data = user_form.cleaned_data
            if data.get('password') and len(data['password']) > 0:
                request.user.set_password(data['password'])
            email_changed = request.user.email != data['email']
            request.user.email = data['email']
            request.user.save()
            if email_changed:
                return HttpResponseRedirect('/accounts/check-your-email/')
                # return render_to_response('accounts/verify.html', {'user':request.user})
            else:
                return HttpResponseRedirect('/')
    return render_to_response('accounts/edit.html', {'form':user_form}, RequestContext(request))
edit = login_required(edit)

def forgot(request):
    if request.method == 'GET':
        email_form = EmailForm()
    elif request.method == 'POST':
        email_form = EmailForm(request.POST)
        if email_form.is_valid():
            pass  # send new mail
    return render_to_response('accounts/forgot.html', {'form':email_form}, RequestContext(request))
        
        
def captcha(request):
    word = request.session['captcha_word']
    from StringIO import StringIO
    #word = makeword(key)
    s = StringIO()
    makeimage(word).save(s, format="png")
    print word
    return HttpResponse(s.getvalue(), 'image/png')
