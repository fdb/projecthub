
from south.db import db
from django.db import models
from projecthub.apps.forum.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'Category'
        db.create_table('forum_category', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField(max_length=100, unique=True)),
            ('position', models.IntegerField()),
        ))
        
        # Mock Models
        Category = db.mock_model(model_name='Category', db_table='forum_category', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        
        # Model 'Forum'
        db.create_table('forum_forum', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('category', models.ForeignKey(Category)),
            ('name', models.CharField(max_length=150, unique=True)),
            ('slug', models.SlugField(unique=True)),
            ('description', models.CharField(max_length=200)),
            ('posting_help', models.TextField(blank=True)),
            ('position', models.IntegerField()),
        ))
        
        # Mock Models
        Forum = db.mock_model(model_name='Forum', db_table='forum_forum', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        
        # Model 'Topic'
        db.create_table('forum_topic', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('forum', models.ForeignKey(Forum)),
            ('title', models.CharField(max_length=150)),
            ('user', models.ForeignKey(User, related_name='forum_topic_set')),
            ('created_at', models.DateTimeField()),
            ('updated_at', models.DateTimeField()),
            ('hits', models.IntegerField(default=0)),
            ('sticky', models.BooleanField(default=False)),
            ('post_count', models.IntegerField(default=0)),
            ('last_reply_at', models.DateTimeField(blank=True, null=True)),
            ('last_reply_author', models.ForeignKey(User, blank=True, null=True)),
            ('locked', models.BooleanField()),
        ))
        
        # Mock Models
        Topic = db.mock_model(model_name='Topic', db_table='forum_topic', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        
        # Model 'Post'
        db.create_table('forum_post', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('topic', models.ForeignKey(Topic)),
            ('body', models.TextField(max_length=3000)),
            ('user', models.ForeignKey(User, related_name='forum_post_set')),
            ('created_at', models.DateTimeField()),
            ('updated_at', models.DateTimeField()),
            ('ip_address', models.IPAddressField(blank=True, null=True)),
            ('is_removed', models.BooleanField(help_text='Is this post inappropriate?')),
        ))
        
        db.send_create_signal('forum', ['Category','Forum','Topic','Post'])
    
    def backwards(self):
        db.delete_table('forum_post')
        db.delete_table('forum_topic')
        db.delete_table('forum_forum')
        db.delete_table('forum_category')
        
