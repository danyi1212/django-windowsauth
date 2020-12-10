from typing import Iterable

from django.contrib import admin, messages

from windows_auth.models import LDAPUser


@admin.register(LDAPUser)
class LDAPUserAdmin(admin.ModelAdmin):
    list_display = ("user", "domain", "last_sync")
    list_filter = ("domain", "last_sync")
    search_fields = ("user__username", "user__email", "domain")

    actions = ("sync",)

    def sync(self, request, queryset: Iterable[LDAPUser]):
        for ldap_user in queryset:
            if ldap_user.sync():
                messages.success(request, f"{ldap_user} successfully synced")
            else:
                messages.error(request, f"{ldap_user} failed to sync")
