from south.db import db
from django.db import models
from django.utils.translation import ugettext_lazy as _
from projecthub.apps.weblog.models import *

class Migration:
    
    def forwards(self):
        
        
        # Mock Models
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        
        # Model 'Entry'
        db.create_table('weblog_entry', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('title', models.CharField(_('title'), max_length=100)),
            ('slug', models.SlugField(_('slug'), unique=True)),
            ('author', models.ForeignKey(User)),
            ('summary', models.TextField(_('summary'), blank=True)),
            ('content', models.TextField(_('content'), blank=True)),
            ('published', models.BooleanField(_('published'), default=True)),
            ('created', models.DateTimeField(_('created'), auto_now_add=True)),
            ('modified', models.DateTimeField(_('modified'), auto_now=True)),
        ))
        
        db.send_create_signal('weblog', ['Entry'])
    
    def backwards(self):
        db.delete_table('weblog_entry')
        
