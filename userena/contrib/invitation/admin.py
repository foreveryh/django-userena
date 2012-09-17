from django.contrib import admin
from models import InvitationRequest
from models import InvitationCode


class InvitationAdmin(admin.ModelAdmin):
    list_display = ['owner', 'acceptor', 'created_at']
    search_fields = ['id', 'owner', 'acceptor']

admin.site.register(InvitationCode, InvitationAdmin)


class InvitationRequestAdmin(admin.ModelAdmin):
    fields = ('invite_code',)
    list_display = ['email', 'invite_code', 'ip', 'is_allowed']
    search_fields = ('email',)
    list_filter = ('is_allowed',)

admin.site.register(InvitationRequest, InvitationRequestAdmin)