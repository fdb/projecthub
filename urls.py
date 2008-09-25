from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.sitemaps import FlatPageSitemap
from django.contrib import admin

from gravital_website.apps.weblog.feeds import WeblogEntryFeed

admin.autodiscover()

feeds = {
    'weblog': WeblogEntryFeed,
}

sitemaps = {
    'flatpages': FlatPageSitemap,
}

urlpatterns = patterns('',
    (r'^weblog/', include('gravital_website.apps.weblog.urls')),
    (r'^forum/', include('gravital_website.apps.forum.urls')),
    (r'^accounts/', include('gravital_website.apps.accounts.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^rss/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
