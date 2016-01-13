from django import template
from eventowlproject import settings

register = template.Library()

@register.assignment_tag
def settings_value(name):
    if name not in settings.TEMPLATE_SETTINGS:
        raise AttributeError('Add desired variable to TEMPLATE_SETTINGS')

    return getattr(settings, name)


@register.filter
def concat(values, sep, title=True):
    return sep.join(str(val).title() for val in values)