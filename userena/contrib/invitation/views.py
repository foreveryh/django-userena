from django.core.urlresolvers import reverse
from django.views.generic.base import View , TemplateResponseMixin
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView
from django.views.generic import RedirectView
from models import InvitationRequest, InvitationCode
from forms import InvitationRequestForm
import settings

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


class InvitationAcceptedView(RedirectView, TemplateResponseMixin):
    """
    When user open the invitation link, redirect a correct view.
    """
    template_name = 'invitation/invalid_invite_code.html'
    url = reverse('invitation_signup')

    def get(self, request, *args, **kwargs):
        """
        """
        if settings.INVITE_MODE:
            invite_code = self.kwargs['code']
            if invite_code and InvitationCode.objects.is_invite_code_valid():
                #redirect to user register page
                pass
            else:
                return self.render_to_response({})
        super(InvitationAcceptedView, self).get(request)






