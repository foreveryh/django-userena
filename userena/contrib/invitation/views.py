from models import InvitationCode
from forms import InvitationRequestForm

def invite(request, success_url=None, form_class=InvitationRequestForm,
           template_name='invitation/invitation_form.html', extra_context=None)
    """
    User can request an invitation.

    User could request a invitation code after leaving a email address. It will be redirect to success URL if the
     invitation form is valid. Render invitation form template.

    **Required arugments: **
    None.

    **Optional arguments: **
    :success_url:
        The URL to redirect to successful registration. Default value is ``None``, ``invitation_complete`` will be
        resolved in this case.

    :form_class:
        A form class to use for invitation. Takes ``request.user`` as first argument to its constructor. Must have an
        ``email`` field. Custom validation can be implemented here.

    :template_name:
        A custom template to use. Default value is ``invitation/invitation_form.html``

    :extra_context:
        A dictionary of variables to add to the template context. Any callable object in this dictionary will be called to
        produce the end result which appears in the context.

    **Template:**
        ``invitation/invitation_form`` or ``template_name`` keyword argument.

    **Context:**
        A ``RequestContext`` instance is used rendering the template. Context, in addition to ``extra_context``, contains:

        :form:
            The invitation form.
    """

    pass
        #if request.method == 'POST':
        #    form = form_class(request.POST, request.FILES)
        #    if form.is_valid():


