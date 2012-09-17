from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

from profiles.forms import SignupFormExtra

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    # Demo Override the signup form with our own, which includes a
    # first and last name.
    # (r'^accounts/signup/$',
    #  'userena.views.signup',
    #  {'signup_form': SignupFormExtra}),

    (r'^accounts/', include('userena.urls')),
    (r'^invitation/', include('userena.contrib.invitation.urls')),
    (r'^messages/', include('userena.contrib.umessages.urls')),
    url(r'^$',
        direct_to_template,
        {'template': 'static/promo.html'},
        name='promo'),
    (r'^i18n/', include('django.conf.urls.i18n')),
)

# Add media and static files
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


