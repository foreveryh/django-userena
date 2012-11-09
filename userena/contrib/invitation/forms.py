# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from models import InvitationRequest, InvitationCode

class InvitationRequestForm(forms.ModelForm):
    """
    User can offer an email for  requesting an invite code
    """
    content = forms.CharField(widget=forms.Textarea(), label='自我介绍')
    class Meta:
        model = InvitationRequest
        fields = ('email', 'content')

class InvitationForm(forms.ModelForm):
  class Meta:
    model = InvitationCode
    fields = ('owner',)
