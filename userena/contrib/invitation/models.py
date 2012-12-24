# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.utils import timezone
from django.contrib.sites.models import RequestSite, Site
from django.db import models
from django.core.mail import send_mail
import settings
from django.template.loader import render_to_string
from django.contrib.auth.models import User
import random
import re
import hashlib


SHA1_RE = re.compile('^[a-f0-9]{%s}$' % settings.INVITE_CODE_SIZE)
def code_generator(size):
    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    code = hashlib.sha1("%s%s" % (timezone.now(), salt)).hexdigest()[:size]
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
            code = code_generator(size=settings.INVITE_CODE_SIZE)
            invitation = self.model(owner=user,invite_code=code)
            invitation.save()
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
        return invitation and invitation.is_usable()

    def is_from_applicant(self, code):
        try:
            invitation_request = InvitationRequest.objects.get(invite_code__invite_code=code)
            email = invitation_request.email
            return email
        except InvitationRequest.DoesNotExist:
            return False


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
        expiration = timezone.now() - datetime.timedelta(settings.EXPIRE_DAYS)
        return self.get_query_set().filter(created_at__gte=expiration)

    def invalid(self):
        """
            Filter invaild invitation.
        """
        expiration = timezone.now() - datetime.timedelta(settings.EXPIRE_DAYS)
        return self.get_query_set().filter(created_at__le=expiration)


class InvitationCode(models.Model):
    class Meta:
      verbose_name = verbose_name_plural = '邀请码'
    owner = models.ForeignKey(User, verbose_name='持有者', related_name='invitations')
    invite_code = models.CharField('邀请码', max_length=40, unique=True)
    acceptor = models.ForeignKey(User, verbose_name='接收者', blank=True, null=True)
    use_time = models.DateTimeField('激活时间', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    objects = InvitationCodeManager()

    def __unicode__(self):
        return '%s create invite code %s at %s' %\
               (self.owner.username, self.invite_code, str(self.created_at.date()))

    def save(self, force_insert=False, force_update=False, using=None):
      if not self.invite_code:
        self.invite_code = code_generator(size=settings.INVITE_CODE_SIZE)
      super(InvitationCode, self).save(force_insert, force_update, using)

    @property
    def url(self):
      return '/accounts/signup/?code=%s' % self.invite_code

    @property
    def _expire_at(self):
        return self.created_at + datetime.timedelta(settings.EXPIRE_DAYS)

    def is_expired(self):
        if settings.EXPIRE_DAYS == 0:
            return False
        else:
            return timezone.now() >= self._expire_at


    def is_usable(self):
        """return  ``True`` if invitation is still valid, ``False`` otherwise
        """
        return self.acceptor is None and not self.is_expired()

    def mark_used(self, acceptor):
        """
            Mark invitation code used.
        """
        if not self.is_usable():
            raise InvitationError('Invitation code is expired.')
        self.acceptor = acceptor
        self.use_time = timezone.now()
        self.save()

    def send_email(self, email, site=None, request=None):
        """
                Send invitation email.

                **Templates:**

                 :invitation/invitation_email_subject.txt:
                    Template used to render the email subject.

                    **Context:**

                    :invitation: ``InvitationCode`` instance ``send_email`` is called on.
                    :site: ``Site`` instance to be used.

                :invitation/invitation_email.txt:
                    Template used to render the email body

                    **Context:**

                    :invitation: ``InvitationCode`` instance ``send_email`` is called on.
                    :expiration_days:   ``INVITATION_EXPIRE_DAYS``  setting.
                    :site: ``Site`` instance to be used.
        """
        if site is None:
            if Site._meta.installed:
                site = Site.objects.get_current()
            elif request is not None:
                site = RequestSite(request)
        subject = render_to_string('invitation/invitation_email_subject.txt',
                {'invitation': self,
                 'site': site})
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        message = render_to_string('invitation/invitation_email.txt', {
            'invitation': self,
            'expiration_days': settings.EXPIRE_DAYS,
            'site': site
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


class InvitationRequest(models.Model):
    class Meta:
      verbose_name = verbose_name_plural = '邀请码请求'
    email = models.EmailField('邮件地址', max_length=100, unique=True, error_messages={'unique':'该邮箱地址已被使用'})
    content = models.CharField('自我介绍', max_length=2048, default='')
    invite_code = models.ForeignKey(InvitationCode, verbose_name='邀请码', blank=True, null=True, on_delete=models.SET_NULL)
    ip = models.IPAddressField('注册IP')
    created_at = models.DateTimeField('创建时间', default=timezone.now)

    def __unicode__(self):
        return '%s request a invitation from ip %s' % (self.email, str(self.ip))


