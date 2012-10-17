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
        return '<a href="/accounts/signup/?code=%s">http://tkq.com/accounts/signup/?code=%s</a>' % \
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
    list_display = ['email', 'invite_code', 'ip', 'created_at']
    search_fields = ('email',)

    actions = ['send_invitation']
    def send_invitation(self, request, queryset):
      admin = User.objects.filter(is_superuser=True)[0]
      for item in queryset:
        code = InvitationCode.objects.generate_invite_code(admin, 1)[0]
        code.send_mail(item.email)
    send_invitation.short_description = '发送邀请'

admin.site.register(InvitationRequest, InvitationRequestAdmin)