import datetime
from django import template
from gravital_website.apps.weblog.models import Entry

register = template.Library()

@register.inclusion_tag('weblog/entry_snippet.html')
def render_latest_blog_entries(num):
    entries = Entry.objects.filter(published=True)[:num]
    return {
        'entries': entries,
    }

@register.inclusion_tag('weblog/month_links_snippet.html')
def render_month_links():
    return {
        'dates': Entry.objects.dates('created', 'month'),
    }