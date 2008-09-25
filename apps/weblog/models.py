from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class Entry(models.Model):
    """A post on a particular subject matter."""
    
    title = models.CharField(_('title'), max_length=100)
    slug = models.SlugField(_('slug'), unique=True)
    author = models.ForeignKey(User)
    summary = models.TextField(_('summary'), blank=True)
    content = models.TextField(_('content'), blank=True)
    published = models.BooleanField(_('published'), default=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        db_table = 'weblog_entry'
        verbose_name = 'entry'
        verbose_name_plural = 'entries'
        ordering = ('-created',)
        
    def __unicode__(self):
        return self.title
        
    def get_absolute_url(self):
        return "/weblog/%s/%s/" % (self.created.strftime("%Y/%b/%d").lower(), self.slug)
