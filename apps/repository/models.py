from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class Library(models.Model):
    """A unit of code, used for distribution."""
    
    name = models.CharField(_('name'), max_length=32)
    author = models.ForeignKey(User)
    summary = models.TextField(_('summary'))
    description = models.TextField(_('content'), blank=True)
    latest_version = models.CharField(_('latest version'), max_length=32, blank=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    
    # Development status
    # Environment
    # Intented Audience
    # License
    # Operating System
    # Programming Language
    # Topic

    class Meta:
        db_table = 'repo_library'
        verbose_name = 'library'
        verbose_name_plural = 'libraries'
        ordering = ('-created',)
        
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return "/repository/%s/" % self.name
        
class Node(models.Model):
    """A block of functionality."""
    
    library = models.ForeignKey(Library)
    name = models.CharField(_('name'), max_length=32)
    summary = models.TextField(_('summary'))
    description = models.TextField(_('content'), blank=True)

    def get_absolute_url(self):
        return "/repository/%s/%s/" % self.library.name, self.name

class Parameter(models.Model):
    """A field on a node that can be set."""
    
    name = models.CharField(_('name'), max_length=32)
