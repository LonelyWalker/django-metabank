from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from forms import EditInterfaceForm


class EditInterface(FormView):
    template_name = 'settings/edit_interface.html'
    form_class = EditInterfaceForm
    success_url = reverse_lazy('settings_network')

    def form_valid(self, form):
        try:
            # TODO: edit interface
            print form.cleaned_data
            messages.success(self.request, _('Unable to save configuration'))

        except Exception:
            messages.error(self.request, _('Confuguration successfully saved'))

        return super(EditInterface, self).form_valid(form)


class Network(TemplateView):
    template_name = 'settings/network.html'

    def get_context_data(self, **kwargs):
        context = super(Network, self).get_context_data(**kwargs)
        # TODO: get real data
        context['interfaces'] = [
            {'name':'eth0', 'ipaddress': '123.123.123.123', 'netmask': '123.123.123.123', 'status': 'up', 'type': 'DHCP'}
        ]
        return context
