from django import template

register = template.Library()

@register.filter
def render_stars(rating):
    """Generate HTML for star ratings."""
    full_stars = int(rating)
    empty_stars = 5 - full_stars
    return '★' * full_stars + '☆' * empty_stars
