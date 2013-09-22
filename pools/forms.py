from django import forms


class AddPool(forms.Form):
    url = forms.CharField(required=True)
    user = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
