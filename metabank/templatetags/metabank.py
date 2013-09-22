from django import template


register = template.Library()


@register.filter(name='get')
def get(d, key):
    if isinstance(d, basestring):
        return '-'
    return d.get(key, {'value': '-'}).get('value', '-')


@register.filter(name='simple_get')
def simple_get(d, key):
    return d.get(key)
