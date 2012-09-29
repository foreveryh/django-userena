from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic.base import View , TemplateResponseMixin, TemplateView
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView
from django.views.generic import RedirectView
from models import InvitationRequest, InvitationCode
from forms import InvitationRequestForm
from django.conf import settings
from userena.views import signup as userena_signup

is_code_valid = InvitationCode.objects.is_invite_code_valid
class InvitationRequestView(CreateView):
    """
    User can request an invitation.

    User could request a invitation code after leaving a email address. It will be redirect to success URL if the
     invitation form is valid. Render invitation form template.

  """
    template_name = "invitation/request_form.html"
    model = InvitationRequest
    form_class = InvitationRequestForm
    success_url = reverse_lazy('invitation_complete')

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
    url = reverse_lazy('invitation_signup')

    def get(self, request, *args, **kwargs):
        """
        """
        if settings.INVITE_MODE:
            invite_code = request.GET.get('code', None)
            if invite_code and is_code_valid(invite_code):
                #redirect to user register page
                url = reverse_lazy('invitation_signup', kwargs={'code': invite_code})
            else:
                return self.render_to_response({})
        return super(InvitationAcceptedView, self).get(request)


class InvitationSignupView(TemplateView):
    """
    Sign up after an invitation is accepted.
    """
    template_name = 'invitation/invalid_invite_code.html'

    def get(self, request, *args, **kwargs):
        if settings.INVITE_MODE :
            invite_code = request.GET.get('code',None)
            if invite_code and is_code_valid(invite_code):
                return userena_signup(request)
            elif not settings.INVITE_ONLY:
                return userena_signup(request)
        else:
            return userena_signup(request)

        return HttpResponseRedirect(reverse('invitation_invite'))
        #return super(InvitationSignupView, self).get(request)

    def post(self, request, *args, **kwargs):
        return userena_signup(request)


