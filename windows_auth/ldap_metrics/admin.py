from django.contrib import admin
from django.db.models import F, ExpressionWrapper, DurationField

from windows_auth.ldap_metrics.models import LDAPUsage
from windows_auth.ldap_metrics.utils import format_bytes


@admin.register(LDAPUsage)
class LDAPUsageAdmin(admin.ModelAdmin):
    date_hierarchy = "timestamp"
    list_display = ("timestamp", "elapsed_time", "domain", "pid", "operations",
                    "sockets", "bytes", "messages", )
    list_filter = ("domain",)
    search_fields = ("domain", "pid")

    fieldsets = (
        ("General", {
            "description": "Connection's general context",
            "fields": ("timestamp", "pid", "domain"),
        }),
        ("Time", {
            "description": "Connection timings",
            "fields": ("elapsed_time", "initial_connection_start_time", "open_socket_start_time",
                       "connection_stop_time", "last_transmitted_time", "last_received_time"),
        }),
        ("Server", {
            "description": "Socket metrics",
            "fields": ("servers_from_pool", "open_sockets", "closed_sockets", "wrapped_sockets"),
        }),
        ("Bytes", {
            "description": "Traffic metrics",
            "fields": ("bytes_transmitted", "bytes_received"),
        }),
        ("Messages", {
            "description": "LDAP Messages counts",
            "fields": ("messages_transmitted", "messages_received"),
        }),
        ("Operations", {
            "description": "LDAP Operations",
            "fields": ("operations", "abandon_operations", "bind_operations", "add_operations", "compare_operations",
                       "delete_operations", "extended_operations", "modify_operations", "modify_dn_operations",
                       "search_operations", "unbind_operations"),
        }),
        ("Referrals", {
            "description": "LDAP Alternate Locations References",
            "fields": ("referrals_received", "referrals_followed", "referrals_connections"),
        }),
        ("Restartable tries", {
            "description": "Restartable connection metrics",
            "fields": ("restartable_failures", "restartable_successes"),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            elapsed_time=ExpressionWrapper(
                F("connection_stop_time") - F("open_socket_start_time"),
                output_field=DurationField()),
        )

    def elapsed_time(self, obj):
        return obj.elapsed_time

    def bytes(self, obj):
        return f'{format_bytes(obj.bytes_received)} / ' + format_bytes(
            obj.bytes_transmitted
        )

    def messages(self, obj):
        return f'{str(obj.messages_received)} / {str(obj.messages_transmitted)}'

    def sockets(self, obj):
        return f'{str(obj.open_sockets)} / {str(obj.closed_sockets)} / ' + str(
            obj.wrapped_sockets
        )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
