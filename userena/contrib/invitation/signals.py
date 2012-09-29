import logging
from django.conf import settings


logger = logging.getLogger(__name__)
def save_acceptor(sender, user, request, **kwargs):
    from models import InvitationCode
    code = request.session.get("invite_code", "abc")
    #logger.debug(code)
    invitation = InvitationCode.objects.get_invite_code(code)
    if invitation is not None:
        invitation.mark_used(user)


def import_signal():
    from userena import signals as userena_signals
    userena_signals.signup_complete.connect(save_acceptor, sender=None, dispatch_uid='save_acceptor_userena')
    if 'langkawi' in settings.INSTALLED_APPS:
        from langkawi import signals as langkawi_signals
        langkawi_signals.connect.connect(save_acceptor, sender=None, dispatch_uid='save_acceptor_langkawi')
