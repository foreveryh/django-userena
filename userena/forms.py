# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.hashcompat import sha_constructor

from userena import settings as userena_settings
from userena.models import UserenaSignup
from userena.utils import get_profile_model

import random

attrs_dict = {'class': 'required'}

USERNAME_RE = ur'([_0-9a-zA-Z\u4e00-\u9fcb]+)'

class SignupForm(forms.Form):
    """
    Form for creating a new user account.

    Validates that the requested username and e-mail is not already in use.
    Also requires the password to be entered twice.

    """
    username = forms.RegexField(regex=USERNAME_RE,
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_(u"Username"),
                                error_messages={'invalid': u'用户名只能包含汉字，字母，数字及下划线',
                                                'required':u'为自己起一个响亮的名字吧'}
    )
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_(u"Email"),
                             error_messages={'invalid': u'请输入一个有效的邮箱地址',
                                            'required':u'请输入一个有效的邮箱地址'}
    )
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                                                           render_value=False),
                                label=_(u"Create password"),
                            error_messages={'invalid': u'请输入正确的密码',
                                            'required':u'请设置你的登录密码',}

    )
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                                                           render_value=False),
                                label=_(u"Repeat password"),
                        error_messages={'invalid': u'请输入正确的密码',
                                        'required':u'请输入正确的密码'}
    )

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already in use.
        Also validates that the username is not listed in
        ``USERENA_FORBIDDEN_USERNAMES`` list.

        """
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            pass
        else:
            raise forms.ValidationError(_('This username is already taken.'))
        if self.cleaned_data['username'].lower() in userena_settings.USERENA_FORBIDDEN_USERNAMES:
            raise forms.ValidationError(_('This username is not allowed.'))
        return self.cleaned_data['username']

    def clean_email(self):
        """ Validate that the e-mail address is unique. """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_('This email is already in use. Please supply a different email.'))
        return self.cleaned_data['email']

    def clean(self):
        """
        Validates that the values entered into the two password fields match.
        Note that an error here will end up in ``non_field_errors()`` because
        it doesn't apply to a single field.

        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_('The two password fields didn\'t match.'))
        return self.cleaned_data

    def save(self, active=False):
        """ Creates a new user and account. Returns the newly created user. """
        username, email, password = (self.cleaned_data['username'],
                                     self.cleaned_data['email'],
                                     self.cleaned_data['password1'])

        active = not userena_settings.USERENA_ACTIVATION_REQUIRED or active
        new_user = UserenaSignup.objects.create_user(username,
                                                     email,
                                                     password,
                                                     active,
                                                     not active)
        return new_user

class SignupFormOnlyEmail(SignupForm):
    """
    Form for creating a new user account but not needing a username.

    This form is an adaptation of :class:`SignupForm`. It's used when
    ``USERENA_WITHOUT_USERNAME`` setting is set to ``True``. And thus the user
    is not asked to supply an username, but one is generated for them. The user
    can than keep sign in by using their email.

    """
    def __init__(self, *args, **kwargs):
        super(SignupFormOnlyEmail, self).__init__(*args, **kwargs)
        del self.fields['username']

    def save(self):
        """ Generate a random username before falling back to parent signup form """
        while True:
            username = sha_constructor(str(random.random())).hexdigest()[:5]
            try:
                User.objects.get(username__iexact=username)
            except User.DoesNotExist: break

        self.cleaned_data['username'] = username
        return super(SignupFormOnlyEmail, self).save()

class SignupFormTos(SignupForm):
    """ Add a Terms of Service button to the ``SignupForm``. """
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _('You must agree to the terms to register.')})

def identification_field_factory(label, error_required):
    """
    A simple identification field factory which enable you to set the label.

    :param label:
        String containing the label for this field.

    :param error_required:
        String containing the error message if the field is left empty.

    """
    return forms.CharField(label=label,
                           widget=forms.TextInput(attrs=attrs_dict),
                           max_length=75,
                           error_messages={'required': _("%(error)s") % {'error': error_required}})

class AuthenticationForm(forms.Form):
    """
    A custom form where the identification can be a e-mail address or username.

    """
    identification = identification_field_factory(_(u"Email"),
                                                  _(u"Please supply your email."))
    password = forms.CharField(label=_(u"Password"),
                               widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                               error_messages={'required':u'请输入你注册时设置的密码'}
    )
    remember_me = forms.BooleanField(widget=forms.CheckboxInput(),
                                     required=False,
                                     label=_(u'Remember me for %(days)s') % {'days': _(userena_settings.USERENA_REMEMBER_ME_DAYS[0])})

    def __init__(self, *args, **kwargs):
        """ A custom init because we need to change the label if no usernames is used """
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        # Dirty hack, somehow the label doesn't get translated without declaring
        # it again here.
        self.fields['remember_me'].label = _(u'Remember me for %(days)s') % {'days': _(userena_settings.USERENA_REMEMBER_ME_DAYS[0])}
        if userena_settings.USERENA_WITHOUT_USERNAMES:
            self.fields['identification'] = identification_field_factory(_(u"Email"),
                                                                         _(u"Please supply your email."))

    def clean(self):
        """
        Checks for the identification and password.

        If the combination can't be found will raise an invalid sign in error.

        """
        identification = self.cleaned_data.get('identification')
        password = self.cleaned_data.get('password')

        if identification and password:
            user = authenticate(identification=identification, password=password)
            if user is None:
                raise forms.ValidationError(_(u"Please enter a correct username or email and password. Note that both fields are case-sensitive."))
        return self.cleaned_data

class ChangeEmailForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_(u"New email"))

    def __init__(self, user, *args, **kwargs):
        """
        The current ``user`` is needed for initialisation of this form so
        that we can check if the email address is still free and not always
        returning ``True`` for this query because it's the users own e-mail
        address.

        """
        super(ChangeEmailForm, self).__init__(*args, **kwargs)
        if not isinstance(user, User):
            raise TypeError, "user must be an instance of User"
        else: self.user = user

    def clean_email(self):
        """ Validate that the email is not already registered with another user """
        if self.cleaned_data['email'].lower() == self.user.email:
            raise forms.ValidationError(_(u'You\'re already known under this email.'))
        if User.objects.filter(email__iexact=self.cleaned_data['email']).exclude(email__iexact=self.user.email):
            raise forms.ValidationError(_(u'This email is already in use. Please supply a different email.'))
        return self.cleaned_data['email']

    def save(self):
        """
        Save method calls :func:`user.change_email()` method which sends out an
        email with an verification key to verify and with it enable this new
        email address.

        """
        return self.user.userena_signup.change_email(self.cleaned_data['email'])

class EditProfileForm(forms.ModelForm):
    """ Base form used for fields that are always required """

    username = forms.RegexField(regex=USERNAME_RE, max_length=30, label=_(u"用户名"),
        error_messages={'invalid': u'用户名只能包含汉字，字母，数字及下划线'})
    description = forms.CharField(widget=forms.Textarea, label=_(u'旅行哲学'), max_length=140)

    class Meta:
        model = get_profile_model()
        exclude = ['user','privacy','mugshot', 'nickname', 'slug', 'tags_history', 'guides', 'birthday', 'old_user',
                   'reputation', 'reputation_base']

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already in use.
        Also validates that the username is not listed in
        ``USERENA_FORBIDDEN_USERNAMES`` list.

        """
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            pass
        else:
            profile = self.instance
            if user == profile.user: pass
            else: raise forms.ValidationError(_('This username is already in use.'))

        if self.cleaned_data['username'].lower() in userena_settings.USERENA_FORBIDDEN_USERNAMES:
            raise forms.ValidationError(_('This username is not allowed.'))
        return self.cleaned_data['username']


    def save(self, force_insert=False, force_update=False, commit=True):
        profile = super(EditProfileForm, self).save(commit=commit)
        # Save Username
        user = profile.user
        user.username = self.cleaned_data['username']
        user.save()
        return profile
