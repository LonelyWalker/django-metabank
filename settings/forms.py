from django import forms
from django.utils.translation import ugettext_lazy as _


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from crispy_forms.bootstrap import FormActions


class EditInterfaceForm(forms.Form):
    type = forms.TypedChoiceField(
        label = _("Type"),
        choices = (('dhcp', _('DHCP')), ('static', _('Static'))),
        widget = forms.RadioSelect,
        initial = 'dhcp',
        required = True,
    )
    ipaddress = forms.IPAddressField(_('IP address'), required=False)
    netmask = forms.IPAddressField(_('Netmask'), required=False)
    gateway = forms.IPAddressField(_('Gateway'), required=False)
    dns1 = forms.IPAddressField(_('First DNS server'), required=False)
    dns2 = forms.IPAddressField(_('Second DNS server'), required=False)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Field('type', disabled=True),
            Field('ipaddress', disabled=True),
            Field('netmask', disabled=True),
            Field('gateway', disabled=True),
            Field('dns1', disabled=True),
            Field('dns2', disabled=True),

            FormActions(
                Submit('submit', 'Submit', css_class="btn-primary")
            )
        )
        super(EditInterfaceForm, self).__init__(*args, **kwargs)


    def clean(self):
        cleaned_data = super(EditInterfaceForm, self).clean()
        t = cleaned_data.get("type")

        if t == 'static':
            for f in ['ipaddress', 'netmask', 'gateway', 'dns1', 'dns2']:
                if not cleaned_data.get(f):
                    self._errors[f] = self.error_class([_('This field is required.')])

        return cleaned_data
