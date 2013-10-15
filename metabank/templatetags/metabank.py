from datetime import datetime
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


@register.filter(name='not_exceed')
def not_exceed(value, seconds=60):
    if int(datetime.now().strftime("%s")) - int(value) < int(seconds):
        return True
    return False

LABELS = {
    'active': 'label-success',
    'stale': 'label-warning',
}
@register.filter
def pool_status_label(status):
    return LABELS.get(status, '')
