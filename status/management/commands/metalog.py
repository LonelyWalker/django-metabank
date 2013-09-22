from django.conf import settings
from django.core.management.base import BaseCommand

from status.models import LogAverage
from cgminer import Client

class Command(BaseCommand):
    help = "collect log data"
    usage_str = "Usage: ./manage.py metalog"

    def handle(self, *args, **options):
        c = Client(getattr(settings, 'CGMINER_HOST', None),
                   getattr(settings, 'CGMINER_PORT', None))

        try:
            summary = c.command('summary')['SUMMARY'][0]
        except Exception:
            summary = {
                'MHS av': 0
            }

        la = LogAverage(
            mhs = summary.get('MHS av'),
        )

        la.save()
