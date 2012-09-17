from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView
from models import InvitationRequest
from forms import InvitationRequestForm

class InvitationRequestView(CreateView):
    """
    User can request an invitation.

    User could request a invitation code after leaving a email address. It will be redirect to success URL if the
     invitation form is valid. Render invitation form template.

  """
    template_name = "invitation/request_form.html"
    model = InvitationRequest
    form_class = InvitationRequestForm
    success_url = '/invitation/complete/'#reverse('invitation_complete')

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def form_valid(self, form):
        client_ip = self.get_client_ip(self.request)
        invitation_request = form.save(commit=False)
        invitation_request.ip = client_ip
        super(InvitationRequestView, self).form_valid(form)











