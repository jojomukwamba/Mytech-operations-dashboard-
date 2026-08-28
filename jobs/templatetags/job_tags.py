from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Access dict values with variable keys in templates."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, 0)
    return getattr(dictionary, str(key), 0)


@register.filter
def pct_of(value, total):
    """Return percentage of value vs total, capped at 100."""
    try:
        v = int(value or 0)
        t = int(total or 0)
        return min(round(v / t * 100), 100) if t else 0
    except (TypeError, ZeroDivisionError):
        return 0


@register.filter
def slugify(value):
    """Convert status strings like 'In Progress' to 'in-progress' for CSS classes."""
    return str(value).lower().replace(' ', '-').replace('/', '-')


@register.filter
def replace_spaces_and_slashes(value):
    """Convert 'In Progress' → 'In_Progress' to match dict keys."""
    return str(value).replace(' ', '_').replace('/', '_')


@register.filter
def zip_choices(choices):
    """Pass-through – choices is already an iterable of (value, label)."""
    return choices


@register.filter
def lower(value):
    return str(value).lower()
