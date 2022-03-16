import os

from django.utils.timezone import make_aware
from ldap3.core.usage import ConnectionUsage

from windows_auth import logger
from windows_auth.ldap import _ldap_connections
from windows_auth.ldap_metrics.models import LDAPUsage
from windows_auth.utils import LogExecutionTime


def format_bytes(value, precision=2, step_size=1024, steps=('B', 'KB', 'MB', 'GB', 'TB')):
    label_index = 0
    while value > step_size and label_index < len(steps):
        label_index += 1  # increment the index of the suffix
        value = value / step_size  # apply the division

    return "%.*f %s" % (precision, value, steps[label_index])


def optional_make_aware(value, timezone=None, is_dst=None):
    if value is not None:
        return make_aware(value, timezone=timezone, is_dst=is_dst)
    else:
        return None


def create_usage(domain: str, usage: ConnectionUsage) -> LDAPUsage:
    logger.debug(f"Collecting LDAP Connection metrics for {domain}")
    return LDAPUsage(
        domain=domain,
        pid=os.getpid(),

        initial_connection_start_time=optional_make_aware(usage.initial_connection_start_time),
        open_socket_start_time=optional_make_aware(usage.open_socket_start_time),
        connection_stop_time=optional_make_aware(usage.connection_stop_time),
        last_transmitted_time=optional_make_aware(usage.last_transmitted_time),
        last_received_time=optional_make_aware(usage.last_received_time),

        servers_from_pool=usage.servers_from_pool,
        open_sockets=usage.open_sockets,
        closed_sockets=usage.closed_sockets,
        wrapped_sockets=usage.wrapped_sockets,

        bytes_transmitted=usage.bytes_transmitted,
        bytes_received=usage.bytes_received,
        messages_transmitted=usage.messages_transmitted,
        messages_received=usage.messages_received,

        operations=usage.operations,
        abandon_operations=usage.abandon_operations,
        bind_operations=usage.bind_operations,
        add_operations=usage.add_operations,
        compare_operations=usage.compare_operations,
        delete_operations=usage.delete_operations,
        extended_operations=usage.extended_operations,
        modify_operations=usage.modify_operations,
        modify_dn_operations=usage.modify_dn_operations,
        search_operations=usage.search_operations,
        unbind_operations=usage.unbind_operations,

        referrals_received=usage.referrals_received,
        referrals_followed=usage.referrals_followed,
        referrals_connections=usage.referrals_connections,

        restartable_failures=usage.restartable_failures,
        restartable_successes=usage.restartable_successes,
    )


def collect_metrics(unbind: bool = True):
    if unbind:
        logger.info("Unbinding all LDAP Connections for collecting metrics")

    with LogExecutionTime("Collecting LDAP Connection metrics"):
        try:
            LDAPUsage.objects.bulk_create(
                create_usage(domain, manager.get_usage())
                for domain, manager in _ldap_connections.items()
                if manager.get_usage(unbind=unbind)
            )
        except Exception as e:
            logger.exception(f"Collection of LDAP Connection Metrics failed: {e}")
