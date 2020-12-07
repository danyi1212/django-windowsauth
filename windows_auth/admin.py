from django.contrib import admin

from windows_auth.models import LDAPUser


@admin.register(LDAPUser)
class LDAPUserAdmin(admin.ModelAdmin):
    list_display = ("user", "domain", "last_sync")
    list_filter = ("domain", "last_sync")
    search_fields = ("user__username", "user__email", "domain")
