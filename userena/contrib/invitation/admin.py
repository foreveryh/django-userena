# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from models import InvitationRequest
from models import InvitationCode
from userena.contrib.invitation.forms import InvitationForm


class InvitationAdmin(admin.ModelAdmin):
    list_display = ['owner', 'invite_code', 'acceptor', 'created_at', 'use_time', 'is_valid', 'link']
    search_fields = ['id', 'owner', 'acceptor']
    actions = ['generate_invitation_10', 'generate_invitation_50']
    form = InvitationForm

    def is_valid(self, obj):
      return obj.is_usable()
    is_valid.short_description = '是否有效'

    def link(self, obj):
      if obj.is_usable():
        return '<a href="/accounts/signup/?code=%s">http://tukeq.com/accounts/signup/?code=%s</a>' % \
             (obj.invite_code, obj.invite_code)
      else:
        return '已使用'
    link.short_description = '邀请链接'
    link.allow_tags = True

    def generate_invitation_10(self, request, queryset):
      # do not care about queryset user selected, just generate code
      InvitationCode.objects.generate_invite_code(request.user, 10)
    generate_invitation_10.short_description = '生成10个邀请码'

    def generate_invitation_50(self, request, queryset):
      # do not care about queryset user selected, just generate code
      InvitationCode.objects.generate_invite_code(request.user, 50)
    generate_invitation_50.short_description = '生成50个邀请码'

admin.site.register(InvitationCode, InvitationAdmin)


class InvitationRequestAdmin(admin.ModelAdmin):
    fields = ('invite_code',)
    list_display = ['email', 'content', 'invite_code', 'ip', 'created_at', 'activated']
    search_fields = ('email',)

    def activated(self, obj):
      code = obj.invite_code
      if code:
        if code.use_time:
          return '已被用户<a href="/accounts/%s/">%s</a>于%s激活' % (code.acceptor.id, code.acceptor.username, code.use_time)
        else:
          return '未激活'
      else:
        return '尚未分配邀请码'
    activated.short_description = '是否激活'
    activated.allow_tags = True

    actions = ['send_invitation']
    def send_invitation(self, request, queryset):
      admin = User.objects.filter(is_superuser=True)[0]
      for item in queryset:
        if item.invite_code:
          code = item.invite_code
        else:
          code = InvitationCode.objects.generate_invite_code(admin, 1)[0]
          item.invite_code = code
          item.save()
        code.send_email(item.email)
    send_invitation.short_description = '发送邀请'

admin.site.register(InvitationRequest, InvitationRequestAdmin)
