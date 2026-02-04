from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import static
from django.urls import reverse
import markdown
import re

register = template.Library()


def process_custom_references(text: str) -> str:
    """
    Process markdown custom protocol references:
    - ![alt](static:path/to/file) -> proper Django static URLs
    - [link text](static:path/to/file) -> proper Django static URLs
    - [link text](c_cipher:1447/7a) -> Django reverse URL to puzzle preview
    - [!alert TYPE|Message] -> DaisyUI alert box HTML
    
    The c_cipher protocol format is: c_cipher:YEAR/DAY[a|b]
    which maps to the puzzle preview URL for that puzzle slug.
    
    The alert format is: [!alert TYPE|Message content]
    where TYPE is: success, danger, info, warning, error, dark
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
    
    def replace_cipher_url(match):
        link_text = match.group(1)
        cipher_path = match.group(2)
        # Convert format like "1447/7a" to slug "1447-7a"
        puzzle_slug = cipher_path.replace('/', '-')
        try:
            puzzle_url = reverse('c_cipher:puzzle_preview', kwargs={'slug': puzzle_slug})
        except:
            # If the URL reverse fails, keep the original format
            return f'[{link_text}]({cipher_path})'
        return f'[{link_text}]({puzzle_url})'
    
    def replace_alert_box(match):
        alert_type = match.group(1).lower()
        message = match.group(2)
        # Validate alert type, default to 'info' if invalid
        valid_types = {'success', 'danger', 'info', 'warning', 'error', 'dark'}
        if alert_type not in valid_types:
            alert_type = 'info'
        return f'<div class="alert alert-{alert_type}">{message}</div>'
    
    # Match ![alt](static:path) and [text](static:path)
    pattern_static = r'(!?)\[([^\]]+)\]\(static:([^\)]+)\)'
    text = re.sub(pattern_static, replace_static_url, text)
    
    # Match [text](c_cipher:YEAR/DAY)
    pattern_cipher = r'\[([^\]]+)\]\(c_cipher:([^\)]+)\)'
    text = re.sub(pattern_cipher, replace_cipher_url, text)
    
    # Match [!alert TYPE|Message content]
    pattern_alert = r'\[!alert\s+([a-zA-Z]+)\|([^\]]+)\]'
    text = re.sub(pattern_alert, replace_alert_box, text)
    
    return text


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
    # Process custom protocol references first (static: and c_cipher:)
    processed = process_custom_references(value)
    html = markdown.markdown(
        processed,
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html5",
    )
    # Add external link attributes
    html = add_external_link_attributes(html)
    return mark_safe(html)
