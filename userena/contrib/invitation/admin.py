from django.contrib import admin
from invitation.models import InvitationCode


class InvitationAdmin(admin.ModelAdmin):
    list_display = ['owner', 'acceptor', 'is_used', 'create_at']
    search_fields = ['id', 'owner', 'acceptor']

admin.site.register(InvitationCode, InvitationAdmin)