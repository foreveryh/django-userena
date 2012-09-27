import logging

logger = logging.getLogger(__name__)
def save_acceptor(sender, user, code, **kwargs):
    from models import InvitationCode
    logger.debug("registered user: %s & code: %s" % (user,code))
    invitation = InvitationCode.objects.get_invite_code(code)
    if invitation is not None:
        invitation.mark_used(user)


def import_signal():
    from userena import signals as userena_signals
    userena_signals.signup_complete.connect(save_acceptor, sender=None, dispatch_uid='save_acceptor')
