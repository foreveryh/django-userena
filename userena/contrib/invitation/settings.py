from django.conf import settings

INVITE_MODE = getattr(settings, 'INVITATION_MODE', False)
INVITE_ONLY = getattr(settings, 'INVITATION_INVITE_ONLY', False)
PENDING_LIMIT = getattr(settings, 'INVITATION_PENDING_LIMIT', 1)
EXPIRE_DAYS = getattr(settings, 'INVITATION_EXPIRE_DAYS', 0) #0 means never expired
DEFAULT_FROM_EMAIL = getattr(settings, 'INVITATION_FROM_EMAIL', 'no-reply@tukeq.com')
INVITE_CODE_SIZE = getattr(settings, 'INVITATION_CODE_SIZE', 20) #MUST BE LESS THAN 40


from userena.contrib.invitation.signals import import_signal
import_signal()