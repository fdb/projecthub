from django.contrib import admin

from models import Category, Forum, Topic, Post

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'position')
    
class ForumAdmin(admin.ModelAdmin):
    list_display = ('category', 'name', 'description', 'position')
    search_fields = ('name', )
    prepopulated_fields = {'slug': ('name', )}

class TopicAdmin(admin.ModelAdmin):
    list_display = ('forum', 'title', 'user')
    search_fields = ('title', )
    raw_id_fields = ('user', )
    
class PostAdmin(admin.ModelAdmin):
    list_display = ('topic', 'user', 'created_at')
    raw_id_fields = ('user', )
    
admin.site.register(Category, CategoryAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Post, PostAdmin)
