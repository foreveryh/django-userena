import datetime
from django.contrib.sites.models import RequestSite, Site
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.models import User
import string
import random
import re
import hashlib


SHA1_RE = re.compile('^[a-f0-9]{40}$')
def code_generator(size=6, username='tukeq'):
    salt = hashlib.sha1(str(random.random())).hexdigest()[1:size]
    code = hashlib.sha1("%s%s%s" % (datetime.datetime.now(), salt, username)).hexdigest()
    return code


class InvitationError(Exception):
    pass


class InvitationCodeManager(models.Manager):
    def generate_invite_code(self, user, num=3):
        """
            Create a batch of invitation code for ``user``
        """
        result_list = []
        for i in range(num):
            code = code_generator()
            invitation = self.model(owner=user,invite_code=code)
            result_list.append(invitation)
        return result_list

    def get_invite_code(self, code):
        """
            Return Invitation key, or None if it doesn't exist.
        """
        if not SHA1_RE.search(code):
            return None
        try:
            invitation = self.get(invite_code=code)
        except self.model.DoesNotExist:
            return None
        return invitation

    def is_invite_code_valid(self, code):
        """
            Check if an ``invite_code`` is valid or not, returning a boolean,
        ``True`` if the code is valid.
        """
        invitation = self.get_invite_code(code)
        return invitation and invite_code.is_usable()

    def remaining_invite_code_for_user(self, user):
        """
            Return the number of remaining invitations for a given ``user``.
        """
        pass

    def delete_expired_invite_code(self):
        for invitation in self.all():
            if invitation.is_expired():
                invitation.delete()

    def valid(self):
        """
            Filter valid invitations
        """
        expiration = datetime.datetime.now() - datetime.timedelta(settings.EXPIRE_DAYS)
        return self.get_query_set().filter(created_at__gte=expiration)

    def invalid(self):
        """
            Filter invaild invitation.
        """
        expiration = datetime.datetime.now() - datetime.timedelta(settings.EXPIRE_DAYS)
        return self.get_query_set().filter(created_at__le=expiration)


class InvitationCode(models.Model):
    owner = models.ForeignKey(User, related_name='invitations')
    invite_code = models.CharField(max_length=40, unique=True)
    acceptor = models.ForeignKey(User, blank=True, null=True)
    use_time = models.DateTimeField()
    created_at = models.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return '%s create invite code %s at %s' %\
               (self.user.username, self.invite_code, str(self.created_at.date()))

    @property
    def _expire_at(self):
        return self.created_at + datetime.timedelta(settings.EXPIRE_DAYS)

    def is_expired(self):
        return datetime.datetime.now() >= self._expire_at

    def is_usable(self):
        """return  ``True`` if invitation is still valid, ``False`` otherwise
        """
        return self.acceptor is None and not self.is_expired()

    def mark_used(self, acceptor):
        """
            Mark invitation code used.
        """
        if self.is_usable():
            raise InvitationError('Invitation code is expired.')
        self.acceptor = acceptor
        self.use_time = datetime.datetime.now
        self.save()


class InvitationRequest(models.Model):
    email = models.EmailField(max_length=100, unique=True)
    is_allowed = models.IntegerField(default=0)
    invite_code = models.ForeignKey(InvitationCode, blank=True, null=True, on_delete=models.SET_NULL)
    ip = models.IPAddressField()
    #created_at = models.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return '%s request a invitation from ip %s' % (self.email, str(self.ip))

    def send_email(self, email=None, site=None, request=None):
        """
                Send invitation email.

                **Templates:**

                 :invitation/invitation_email_subject.txt:
                    Template used to render the email subject.

                    **Context:**

                    :invitation: ``Invitation`` instance ``send_email`` is called on.
                    :site: ``Site`` instance to be used.

                :invitation/invitation_email.txt:
                    Template used to render the email body

                    **Context:**

                    :invitation: ``Invitation`` instance ``send_email`` is called on.
                    :expiration_days:   ``INVITATION_EXPIRE_DAYS``  setting.
                    :site: ``Site`` instance to be used.
        """
        email = email or self.email
        if site is None:
            if Site._meta.installed:
                site = Site.objects.get_current()
            elif request is not None:
                site = RequestSite(request)
        subject = render_to_string('invitation/invitation_email_subject.txt',
            {'invitation': self, 'site': site})
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        message = render_to_string('invitation/invitation_email.txt', {
            'invitation': self,
            'expiration_days': settings.EXPIRE_DAYS,
            'site': site
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
