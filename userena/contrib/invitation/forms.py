from django import forms


class InvitationRequestForm(forms.Form):
    email = forms.EmailField()