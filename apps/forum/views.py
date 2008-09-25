from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django import forms
from django.contrib.auth.decorators import login_required
from models import Category, Forum, Topic, Post

class TopicForm(forms.Form):
    title = forms.CharField()
    body = forms.CharField(widget=forms.Textarea(attrs={'rows':'15', 'cols':'60'}))


class TopicTitleForm(forms.Form):
    title = forms.CharField()

class PostForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea(attrs={'rows':'15', 'cols':'60'}))

def list_forums(request):
    categories = Category.objects.all()
    return render_to_response('forum/forum_list.html', {'categories':categories}, RequestContext(request))
    
def list_topics(request, forum_slug):
    forum = get_object_or_404(Forum, slug=forum_slug)
    return render_to_response('forum/topic_list.html', {'forum':forum}, RequestContext(request))
    
def new_topic(request, forum_slug):
    forum = get_object_or_404(Forum, slug=forum_slug)
    if request.method == 'GET':
        topic_form = TopicForm()
    elif request.method == 'POST':
        topic_form = TopicForm(request.POST)
        if topic_form.is_valid():
            data = topic_form.cleaned_data
            new_topic = Topic(forum=forum, title=data['title'], user=request.user)
            new_topic.save()
            new_post = Post(topic=new_topic, body=data['body'], user=request.user, ip_address=request.META.get('REMOTE_ADDR'))
            new_post.save()
            return HttpResponseRedirect(new_topic.get_absolute_url())
    return render_to_response('forum/topic_new.html', {'forum':forum, 'form':topic_form}, RequestContext(request))
new_topic = login_required(new_topic)

def edit_topic(request, forum_slug, topic_id):
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, pk=topic_id)
    if request.method == 'GET':
        topic_title_form = TopicTitleForm(topic.__dict__)
    elif request.method == 'POST':
        topic_title_form = TopicTitleForm(request.POST)
        if topic_title_form.is_valid():
            data = topic_title_form.cleaned_data
            topic.title = data['title']
            topic.save()
            return HttpResponseRedirect(topic.get_absolute_url())
    return render_to_response('forum/topic_edit.html', {'forum':forum, 'topic':topic, 'form':topic_title_form}, RequestContext(request))
edit_topic = login_required(edit_topic)

def list_posts(request, forum_slug, topic_id):
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, pk=topic_id)
    return render_to_response('forum/post_list.html', {'forum':forum, 'topic':topic}, RequestContext(request))

def new_post(request, forum_slug, topic_id):
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, pk=topic_id)
    if request.method == 'GET':
        post_form = PostForm()
    elif request.method == 'POST':
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            data = post_form.cleaned_data
            new_post = Post(topic=topic, body=data['body'], user=request.user, ip_address=request.META.get('REMOTE_ADDR'))
            new_post.save()
            return HttpResponseRedirect(topic.get_absolute_url())
    return render_to_response('forum/post_new.html', {'forum':forum, 'topic':topic, 'form':post_form}, RequestContext(request))
new_post = login_required(new_post)

def edit_post(request, forum_slug, topic_id, post_id):
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, pk=topic_id)
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'GET':
        post_form = PostForm(post.__dict__)
    elif request.method == 'POST':
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            data = post_form.cleaned_data
            post.body = data['body']
            post.save()
            return HttpResponseRedirect(topic.get_absolute_url())
    return render_to_response('forum/post_edit.html', {'forum':forum, 'topic':topic, 'form':post_form}, RequestContext(request))
        
edit_post = login_required(edit_post)

