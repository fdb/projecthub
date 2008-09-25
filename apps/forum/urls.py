from django.conf.urls.defaults import *
from models import Category, Forum, Topic, Post

category_info_dict = {
    'queryset': Category.objects.all(),
}

forum_info_dict = {
    'queryset': Forum.objects.all(),
}

topic_info_dict = {
    'queryset': Topic.objects.all(),
}

urlpatterns = patterns('gravital_website.apps.forum.views',
    (r'^/?$', 'list_forums'),
    (r'^(?P<forum_slug>[a-z\-]+)/$', 'list_topics'),
    (r'^(?P<forum_slug>[a-z\-]+)/new/$', 'new_topic'),
    (r'^(?P<forum_slug>[a-z\-]+)/(?P<topic_id>[0-9]+)/$', 'list_posts'),
    (r'^(?P<forum_slug>[a-z\-]+)/(?P<topic_id>[0-9]+)/edit/$', 'edit_topic'),
    (r'^(?P<forum_slug>[a-z\-]+)/(?P<topic_id>[0-9]+)/reply/$', 'new_post'),
    (r'^(?P<forum_slug>[a-z\-]+)/(?P<topic_id>[0-9]+)/(?P<post_id>[0-9]+)/edit/$', 'edit_post'),
)
