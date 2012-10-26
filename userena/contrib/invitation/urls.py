from django.conf.urls import *
from django.views.generic import TemplateView
from userena.contrib.invitation import views as invitation_views

urlpatterns = patterns('',
    url(r'^complete/$',TemplateView.as_view(template_name='invitation/invitation_complete.html'),
        name='invitation_complete'
    ),
    url(r'^apply/$',invitation_views.InvitationRequestView.as_view(),
        name='invitation_invite'),
    url(r'^accepted/%s/$' %(r'(?P<code>[\-_0-9a-zA-Z\.]+)') ,invitation_views.InvitationAcceptedView.as_view(),
        name='invitation_invited'),
    url(r'^signup/$', invitation_views.InvitationSignupView.as_view(), name='invitation_signup'),
)
