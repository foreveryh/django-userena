from django.conf import settings


INVITE_ONLY = getattr(settings, 'INVITATION_INVITE_ONLY', False)
PENDING_LIMIT = getattr(settings, 'INVITATION_PENDING_LIMIT', 1)
EXPIRE_DAYS = getattr(setttings, 'INVITATION_EXPIRE_DAYS', 30)
