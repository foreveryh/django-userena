from django.forms import ModelForm
from django.forms.fields import EmailField
from models import InvitationRequest, InvitationCode

class InvitationRequestForm(ModelForm):
    """
    User can offer an email for  requesting an invite code
    """
    class Meta:
        model = InvitationRequest
        fields = ('email', 'content')

class InvitationForm(ModelForm):
  class Meta:
    model = InvitationCode
    fields = ('owner',)
