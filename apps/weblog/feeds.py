from django.contrib.syndication.feeds import Feed
from models import Entry
import datetime

class WeblogEntryFeed(Feed):
    title = "The Gravital weblog"
    link = "http://www.gravital.net/weblog/"
    description = "Latest news about Gravital, the graphic design application for hackers."

    def items(self):
        return Entry.objects.filter(published=True)[:10]

