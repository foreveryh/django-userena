# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from models import InvitationRequest, InvitationCode

class InvitationRequestForm(forms.ModelForm):
    """
    User can offer an email for  requesting an invite code
    """
    email = forms.EmailField(error_messages={'invalid': '请输入正确的邮箱地址'})
    content = forms.CharField(widget=forms.Textarea(), label='自我介绍', error_messages={'required':'简单介绍一下你的旅行经历吧'})
    class Meta:
        model = InvitationRequest
        fields = ('email', 'content')

class InvitationForm(forms.ModelForm):
  class Meta:
    model = InvitationCode
    fields = ('owner',)
