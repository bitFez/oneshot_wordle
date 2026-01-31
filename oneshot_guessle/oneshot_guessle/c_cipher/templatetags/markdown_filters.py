from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import static
import markdown
import re

register = template.Library()


def process_static_references(text: str) -> str:
    """
    Process markdown static file references like ![alt](static:path/to/file) 
    and convert them to proper Django static URLs.
    
    Also handles [link text](static:path/to/file)
    """
    def replace_static_url(match):
        is_image = match.group(1) == "!"
        alt_text = match.group(2) if is_image else match.group(2)
        static_path = match.group(3)
        static_url = static(static_path)
        
        if is_image:
            return f'![{alt_text}]({static_url})'
        else:
            return f'[{alt_text}]({static_url})'
    
    # Match ![alt](static:path) and [text](static:path)
    pattern = r'(!?)\[([^\]]+)\]\(static:([^\)]+)\)'
    return re.sub(pattern, replace_static_url, text)


def add_external_link_attributes(html: str) -> str:
    """
    Add target="_blank" and rel="noopener noreferrer" to all external links.
    Preserves internal links and static file links.
    """
    def replace_anchor(match):
        href = match.group(1)
        content = match.group(2)
        
        # Don't modify anchors and static files
        if href.startswith('#') or href.startswith('/'):
            return match.group(0)
        
        return f'<a href="{href}" target="_blank" rel="noopener noreferrer">{content}</a>'
    
    # Match all anchor tags with href
    pattern = r'<a href="([^"]+)">([^<]+)</a>'
    return re.sub(pattern, replace_anchor, html)


@register.filter(name="markdownify")
def markdownify(value: str) -> str:
    if value is None:
        return ""
    # Process static file references first
    processed = process_static_references(value)
    html = markdown.markdown(
        processed,
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html5",
    )
    # Add external link attributes
    html = add_external_link_attributes(html)
    return mark_safe(html)
