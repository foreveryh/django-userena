from django.conf.urls import *
from django.views.generic import TemplateView
from invitation.views import *

urlpatterns = patterns('',
    url(r'^invite/complete/$',
        TemplateView.as_view(template_name='invitation/invitation_complete.html'),
        name='invitation_complete'
    ),
    url(r'^invite/$', invite, name='invitation_invite'),
    url(r'^code/(?P<invite_code>\w+)/$', invited, name='invitation_invited'),
    url(r'^signup/$', signup, name='invitation_signup'),
)
