import datetime

from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

class Category(models.Model):
    """Category of a forum, e.g. General, Discussion, Bugs"""
    name = models.CharField(max_length=100, unique=True)
    position = models.IntegerField()
    
    class Meta:
        verbose_name_plural = 'categories'
        ordering = ('position',)

    def __unicode__(self):
        return self.name
    
class Forum(models.Model):
    category = models.ForeignKey(Category)
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=200)
    posting_help = models.TextField(blank=True)
    position = models.IntegerField()
    
    class Meta:
        ordering = ('category', 'position',)
    
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return "/forum/%s/" % self.slug

class Topic(models.Model):
    forum = models.ForeignKey(Forum)
    title = models.CharField(max_length=150)
    user = models.ForeignKey(User, related_name='forum_topic_set')
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    hits = models.IntegerField(default=0)
    sticky = models.BooleanField(default=False)
    post_count = models.IntegerField(default=0)
    last_reply_at = models.DateTimeField(blank=True, null=True)
    last_reply_author = models.ForeignKey(User, blank=True, null=True)
    locked = models.BooleanField()
    
    def save(self):
        if not self.id:
            self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        super(Topic, self).save()
        
    def _get_replies_count(self):
        return self.post_count - 1
    replies_count = property(_get_replies_count)
    
    class Meta:
        pass

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return "/forum/%s/%s/" % (self.forum.slug, self.id)
    
class Post(models.Model):
    topic = models.ForeignKey(Topic)
    body = models.TextField(max_length=3000)
    user = models.ForeignKey(User, related_name='forum_post_set')
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    ip_address = models.IPAddressField(blank=True, null=True)
    is_removed = models.BooleanField(help_text='Is this post inappropriate?')
    
    def save(self):
        if not self.id:
            self.created_at = datetime.datetime.now()
            new_record = True
        else:
            new_record = False
        self.updated_at = datetime.datetime.now()
        super(Post, self).save()
        if new_record:
            self.topic.post_count += 1
            self.topic.save()
    
    class Meta:
        get_latest_by = 'created_at'
        ordering = ('created_at',)
        
    def __unicode__(self):
        return "%s: %s" % (self.topic, self.user)

    def get_absolute_url(self):
        return "/forum/%s/%s/%s/" % (self.topic.forum.slug, self.topic.id, self.id)

