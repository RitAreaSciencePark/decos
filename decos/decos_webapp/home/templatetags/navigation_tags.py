from django import template

# import site:
from wagtail.models import Site

register = template.Library()

# ... keep the definition of get_footer_text and add the get_site_root template tag:
@register.simple_tag(takes_context=True)
#def get_site_root(context):
#    return Site.find_for_request(context["request"]).root_page
def get_site_root(context):
    # Check if 'request' is in the context to avoid KeyError during error page rendering
    if 'request' in context:
        return Site.find_for_request(context["request"]).root_page
    else:
        # Fallback: return the root page of the default site or None
        # You can customize this based on your needs (e.g., Site.objects.get(is_default_site=True).root_page)
        try:
            return Site.objects.get(is_default_site=True).root_page
        except Site.DoesNotExist:
            return None  # Or handle as appropriate

@register.filter
def classname(obj):
    return obj.__class__.__name__.lower()