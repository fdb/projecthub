from django.conf import settings

def primary_links_to_context(request):
    """Load navigation in the template"""
    return {'PRIMARY_LINKS':settings.PRIMARY_LINKS}