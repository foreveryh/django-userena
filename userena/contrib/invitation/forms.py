from django.forms import ModelForm
from django.forms.fields import EmailField
from models import InvitationRequest

class InvitationRequestForm(ModelForm):
    """
    User can offer an email for  requesting an invite code
    """
    class Meta:
        model = InvitationRequest
        fields = ('email',)