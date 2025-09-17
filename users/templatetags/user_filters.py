from django import template

register = template.Library()

@register.filter
def partially_hide(value):
    if "@" in value:
        parts = value.split('@')
        local_part = parts[0]
        domain = parts[1]
        if len(local_part) > 2:
            return f"{local_part[:2]}...@{domain}"
        return f"{local_part[0]}...@ {domain}"
    else:
        if len(value) > 4:
            return f"...{value[-4:]}"
    return value