from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from models import Entry

class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'modified', 'published')
    search_fields = ('title', 'content')
    list_filter = ('published',)
    
admin.site.register(Entry, EntryAdmin)
