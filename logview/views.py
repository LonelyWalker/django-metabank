from django.views.generic.base import TemplateView
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext_lazy as _


FILES = {
    'cgminer': '/var/log/cgminer.log',
    'syslog': '/var/log/syslog',
    'metabank': '/var/log/metabank.log'
}

ONPAGE_DEFAULT = 100


class LogView(TemplateView):
    template_name = 'logview/log.html'

    def get_context_data(self, **kwargs):
        context = super(LogView, self).get_context_data(**kwargs)

        # validate file
        logfile = self.request.GET.get('file')
        if logfile not in FILES:
            logfile = 'cgminer'

        # validate lines
        try:
            onpage = int(self.request.GET.get('onpage', ONPAGE_DEFAULT))
        except ValueError:
            onpage = ONPAGE_DEFAULT

        if onpage < 10: onpage = ONPAGE_DEFAULT

        try:
            f = open(FILES[logfile], 'r')
            lines = list(reversed(f.readlines()))
        except IOError:
            lines = [_('Can\'t open the file')]
        finally:
            try:
                f.close()
            except Exception:
                pass

        paginator = Paginator(lines, onpage)

        try:
            lines = paginator.page(self.request.GET.get('page', 1))
        except (EmptyPage, InvalidPage):
            lines = paginator.page(paginator.num_pages)

        context['lines'] = lines
        context['files'] = FILES
        context['file'] = logfile
        context['onpage'] = onpage

        return context
